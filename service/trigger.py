import rpyc
import janus
import argparse
import threading
from rpyc.utils.server import ThreadedServer
from rpyc.utils.helpers import classpartial

from helper import *

# Configure service host address and port here
SERVICE_HOST = 'localhost'
SERVICE_PORT = 2100

logger = logging.getLogger('main')


class TriggerService(rpyc.Service):

    def __init__(self, send_jq):
        self._send_jq = send_jq

    def exposed_put(self, **kwargs):
        """Exposed put method

        Args:
            kwargs args sent from sender program
        """
        if kwargs.get('stop', None):
            self._send_jq.sync_q.put(None)
        else:
            self._send_jq.sync_q.put('{} {}'.format(kwargs['state'], kwargs['machine']))


def loop_in_thread(loop, args, que):
    """Run event loop in a separate thread.

    Args:
        loop: event loop
        args (NameSpace): command line arguments
        que (Queue): Queue to hold asynchronous events
    """
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send(loop, args, que))
    logger.info('Exiting loop in thread.')


async def send(loop, args, jq):
    """Trigger service to send events to the notification service

    Args:
        loop: event loop
        args (NameSpace): command line arguments
        jq (Queue): Queue to put the events

    Raises:
         CancelledError - when cou-routine task cancels
         IncompleteReadError, ConnectionResetError - When trigger disconnects to the
         notification service
    """
    reader, writer = await asyncio.open_connection(host=args.host, port=args.port,
                                                   loop=loop)
    logger.debug('%s @%s', args.name, writer.transport.get_extra_info('sockname'))
    try:
        # Handshake between server and trigger
        logger.info('Sending hello message to server.')
        await send_msg(writer, 'Trigger hello')

        logger.info('Waiting for hello message from server')
        message = await read_msg(reader)

        if message and message.lower() == 'hello':
            logger.info('Received reply from server. Sending \'trigger\' as subscription')
            await send_msg(writer, 'trigger')

        logger.debug('Sending events...')
        while True:
            _item = await jq.async_q.get()

            if not _item:
                break

            state, machine = _item.split(' ')
            logger.info('Sending[%s][%s]', state, machine)
            await send_msg(writer, '{} {}'.format(state, machine))
    except asyncio.CancelledError:
        logger.debug('Stopping trigger')
        writer.write_eof()
    except (asyncio.streams.IncompleteReadError, ConnectionResetError):
        logger.debug('Disconnected to Server')
    finally:
        logger.info('Terminating trigger')
        writer.close()


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description='''Trigger application which sends random state and machine name to 
                                                 publisher''')
    cli.add_argument('--host', help='Host IP of the server', default='127.0.0.1')
    cli.add_argument('--port', type=int, help='Port in which server is listening to',
                     default=1200)
    cli.add_argument('--name', help='Name of the trigger', default='mysql-trigger')
    cli.add_argument('-v', '--verbose', action="store_true", help='Enable Verbose mode')
    _args = cli.parse_args()

    # Client name should be lesser than 15 characters
    if len(_args.name) > 15:
        _args.name = _args.name[:16]

    # Setup logging
    setup_logging(log_name=os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'log', 'trigger.log')),
        default_level=logging.DEBUG if _args.verbose else logging.INFO)
    logger.info('Trigger pid: %s', os.getpid())
    logger.info(_args)

    sender_loop = asyncio.get_event_loop()
    queue = janus.Queue()

    # Runs event loop on a thread
    a_thread = threading.Thread(target=loop_in_thread, args=(sender_loop, _args, queue))
    a_thread.start()

    service = classpartial(TriggerService, send_jq=queue)
    ThreadedServer(service, SERVICE_HOST, port=SERVICE_PORT).start()
