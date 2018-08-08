import socket
import argparse
from time import sleep
from helper import *

# Notification framework
handle_notification = True
try:
    import pgi

    pgi.install_as_gi()
    pgi.require_version('Notify', '0.7')
    from pgi.repository import Notify
except ImportError:
    handle_notification = False

logger = logging.getLogger('main')


class Client(object):

    def __init__(self, name, host, port, subscription):
        self._name = name
        self._host = host
        self._port = port
        self._subscription = subscription

    @property
    def name(self):
        return self._name

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def subscription(self):
        return self._subscription

    async def listener(self, loop, subscription):
        reader, writer = await asyncio.open_connection(host=self.host, port=self.port,
                                                       loop=loop)
        logger.debug('%s @%s', self.name, writer.transport.get_extra_info('sockname'))
        short = subscription[:2]
        try:
            # Handshake between server and client
            logger.info('[%s]Sending %s hello message to server.', short, self.name)
            await send_msg(writer, self.name + ' hello')

            logger.info('[%s]Waiting for hello message from server', short)
            message = await read_msg(reader)

            if message and message.lower() == 'hello':
                logger.info('[%s]Received reply from server. Sending Subscription '
                            'info...', short)
                await send_msg(writer, subscription)

            while True:
                data = await read_msg(reader)
                if data:
                    logger.info('[Server][%s]: %s', subscription, data)
                    if handle_notification: show(subscription, data)

        except asyncio.CancelledError:
            logger.debug('Stopping listener for \'%s\'', subscription)
            writer.write_eof()
        finally:
            writer.close()

    def run(self):
        _loop = asyncio.get_event_loop()
        _loop.add_signal_handler(getattr(signal, 'SIGTERM'), exit_handler)

        # Create separate listeners for each subscription
        for sub in self.subscription:
            _loop.create_task(self.listener(_loop, sub))
        try:
            logger.debug('Starting client event loop')
            _loop.run_forever()
        finally:
            logger.debug('Event loop terminated.')
            tasks = asyncio.Task.all_tasks()
            group = asyncio.gather(*tasks, return_exceptions=True)
            group.cancel()
            _loop.run_until_complete(group)
            _loop.close()

    def __str__(self):
        return 'Client \'{}\' Status:\nConnected to Server: {}@{}\nSubscriptions: {}' \
            .format(self.name, self.host, self.port, ', '.join(self.subscription))


def show(title, message):
    notification = Notify.Notification.new(title, message, get_icon(title))
    notification.show()
    sleep(3)
    notification.close()


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description='''
                                     Client application to receive machine state 
                                     notification from the server. 
                                     Client should subscribe to the required states 
                                     that it requires the 
                                     notification
                                  ''')
    cli.add_argument('--host', help='Host IP of the server', default='127.0.0.1')
    cli.add_argument('--port', type=int, help='Port in which server is listening to',
                     default=1200)
    cli.add_argument('--name', help='Name of the client', default=socket.gethostname())
    cli.add_argument('--sub', choices=['Pending', 'Imaging', 'Executing', 'Error',
                                       'Completed', 'Suspended'],
                     nargs='+', default=['Error'], help='Client subscription state')
    args = cli.parse_args()

    # Client name should be lesser than 15 characters
    if len(args.name) > 15:
        args.name = args.name[:16]

    # Setup logging
    setup_logging(log_name=os.path.abspath(os.path.join('log', args.name + '.log')))
    logger.info('Client pid: %s', os.getpid())
    logger.info(args)
    this = Client(name=args.name, host=args.host, port=args.port, subscription=args.sub)

    if handle_notification:
        Notify.init('Client Notifier')

    logger.info('%s %s notification(s)', this.name,
                'shows' if handle_notification else 'doesn\'t show')
    this.run()
    if handle_notification:
        Notify.uninit()  # Un-initialize notification
