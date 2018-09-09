import socket
import argparse
import time

from asyncio import Queue
from helper import *

logger = logging.getLogger('main')

receive_queue = Queue(25)


class Client(object):

    def __init__(self, name, host, port, subscription):
        """Initialize client object with required parameters

        Args:
            name (str): Clients name
            host (str): Host IP Address
            port (int): Port number
            subscription (list): List of client subscriptions
        """
        self._name = name
        self._host = host
        self._port = port
        self._subscription = subscription
        self._attempts = 6

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
        """Create a connection to the server for each subscription

        Args:
            loop: event loop
            subscription (str): One of clients subscription
        """
        global once
        short = subscription[:2]

        # Connecting to Server
        for i in range(1, self._attempts):
            try:
                logger.debug('[%s] Reaching server(attempt=%s)...', short, str(i))
                reader, writer = await asyncio.open_connection(host=self.host,
                                                               port=self.port,
                                                               loop=loop)
                if reader and writer:
                    logger.debug('%s @%s', self.name,
                                 writer.transport.get_extra_info('sockname'))
                    break
            except ConnectionRefusedError:
                time.sleep(10)
                logger.debug('[%s] Attempt %s failed. Retrying..', short, str(i))
        else:
            logger.info('[%s] Could not reach server.', short)
            # Send error notification only once on connection error
            if once:
                once = False
                show('Error', 'Connection to Server failed.')

            loop.stop()
            return

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

            loop.create_task(send_notification())
            while True:
                data = await read_msg(reader)
                if data:
                    logger.info('[Server][%s]: %s', subscription, data)
                    await receive_queue.put((subscription, data))
        except asyncio.CancelledError:
            logger.debug('Stopping listener for \'%s\'', subscription)
            writer.write_eof()
        finally:
            writer.close()

    def run(self):
        """Create a listener for each client subscription

        Raises:
            NotImplementedError - When running on windows operating system
        """
        _loop = asyncio.get_event_loop()
        try:
            # Registering exit handler
            for sig in ('SIGTERM', 'SIGINT'):
                _loop.add_signal_handler(getattr(signal, sig), exit_handler)
        except NotImplementedError:
            logger.info('Signal handling ignored in Windows')

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


async def send_notification():
    """Send data to toast notification

    Retrieves data from queue and send data to toast notification
    Raises:
        CancelledError
    """
    try:
        while True:
            _msg = await receive_queue.get()
            if _msg:
                show(*_msg)
            else:
                logger.error('Send notification received \'None\' for %s', _msg[0])
    except asyncio.CancelledError:
        logger.debug('Stopping send notification.')


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
    cli.add_argument('-v', '--verbose', action="store_true", help='Enable Verbose mode')
    args = cli.parse_args()

    # Client name should be lesser than 15 characters
    if len(args.name) > 15:
        args.name = args.name[:16]

    # Setup logging
    setup_logging(log_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                                        'log', args.name + '.log')),
                  default_level=logging.DEBUG if args.verbose else logging.INFO)
    logger.info('Client pid: %s', os.getpid())
    logger.info(args)
    this = Client(name=args.name, host=args.host, port=args.port, subscription=args.sub)
    this.run()
