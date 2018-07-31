import os
import asyncio
import signal
import json
import functools
import logging.config

from random import randint


logger = logging.getLogger('main')


async def echo_server(reader, writer):
    try:
        # Receive Hello message from client
        data = await reader.readline()

        message = data.decode()
        logger.info('Received %s from client' % message)

        if message and message.lower() == 'hello':
            logger.info('Sending hello message back to client.')
            writer.write('hello\n'.encode())
            await writer.drain()

        # Receive Start message from client
        data = await reader.readline()

        message = data.decode()
        logger.info('Received %s from client' % message)

        if message and message.lower() == 'start':
            logger.info('Received start message from client.')

        # Start sending events to client
        while True:
            data = get_random_server_state()
            logger.info('Sending: %s', data)
            writer.write(data.encode())
            await writer.drain()
            await asyncio.sleep(5)

    except asyncio.CancelledError:
        logger.debug('Stopping Co-routine')
        writer.write_eof()
    finally:
        writer.close()


def get_random_server_state():
    state = ['ERROR', 'SUSPENDED', 'COMPLETED']
    return state[randint(0, len(state) - 1)] + '-HIGH' + str(randint(10,18)) + '\n'


def exit_handler(sig):
    logger.debug('Received signal %s' % sig)
    loop = asyncio.get_event_loop()
    loop.stop()
    loop.remove_signal_handler(signal.SIGTERM)


def main():
    _loop = asyncio.get_event_loop()
    _loop.add_signal_handler(getattr(signal, 'SIGTERM'), functools.partial(exit_handler, signal.SIGTERM))
    co_routine = asyncio.start_server(echo_server, host='127.0.0.1', port=1200,
                                      loop=_loop)
    server = _loop.run_until_complete(co_routine)
    try:
        logger.debug('Starting event loop')
        _loop.run_forever()
    finally:
        logger.debug('Event loop terminated.')
        server.close()
        tasks = asyncio.Task.all_tasks()
        group = asyncio.gather(*tasks, return_exceptions=True)
        group.cancel()
        _loop.run_until_complete(group)
        _loop.close()


def setup_logging(default_path='log_config.json', default_level=logging.INFO):
    """Setup logging configuration"""

    path = default_path
    if os.path.exists(path):
        with open(path, 'r') as f:
            config = json.load(f)
        config['handlers']['file']['filename'] = os.path.abspath(os.path.join('log', 'server.log'))
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


if __name__ == '__main__':
    # Setup logging
    setup_logging()
    logger.info('Server pid: %s', os.getpid())
    main()
