import socket
import argparse

from random import randint
from helper import *

logger = logging.getLogger('main')


def get_random_state_machine():
    state = ['Completed', 'Error', 'Executing', 'Imaging', 'Pending', 'Suspended']
    return state[randint(0, len(state) - 1)], 'HIGH' + str(randint(10, 18))


async def send(args):
    loop = asyncio.get_event_loop()
    reader, writer = await asyncio.open_connection(host=args.host, port=args.port,
                                                   loop=loop)
    logger.debug('%s @%s', args.name, writer.transport.get_extra_info('sockname'))
    try:
        # Handshake between server and client
        logger.info('Sending hello message to server.')
        await send_msg(writer, 'Trigger hello')

        logger.info('Waiting for hello message from server')
        message = await read_msg(reader)

        if message and message.lower() == 'hello':
            logger.info('Received reply from server. Sending events...')

        for i in range(1, args.count + 1):
            state, machine = get_random_state_machine()
            logger.info('[%s]:Sending[%s][%s]', i, state, machine)
            await send_msg(writer, '{} {}'.format(state, machine))
    except asyncio.CancelledError:
        logger.debug('Stopping trigger')
        writer.write_eof()
    finally:
        writer.close()


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description='''Trigger application which sends random state and machine name to 
                                                 publisher''')
    cli.add_argument('--host', help='Host IP of the server', default='127.0.0.1')
    cli.add_argument('--port', type=int, help='Port in which server is listening to',
                     default=1200)
    cli.add_argument('--name', help='Name of the client', default=socket.gethostname())
    cli.add_argument('--num', dest='count', type=int, help='Number of notifications to send', default=100)
    _args = cli.parse_args()

    # Client name should be lesser than 15 characters
    if len(_args.name) > 15:
        _args.name = _args.name[:16]

    # Setup logging
    setup_logging(log_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'log', 'trigger.log')))
    logger.info('Trigger pid: %s', os.getpid())
    logger.info(_args)

    _loop = asyncio.get_event_loop()
    try:
        logger.debug('Starting event loop')
        _loop.run_until_complete(send(_args))
    finally:
        logger.debug('Event loop terminated.')
        _loop.close()
