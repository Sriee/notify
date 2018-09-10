import argparse

from asyncio import Queue
from collections import defaultdict, deque
from helper import *

logger = logging.getLogger('main')

subscriber = defaultdict(deque)  # [k: String, v: Deque]
send_queue = defaultdict(Queue)  # [k: Writer, v: Queue]
state_queue = {}                 # [k: String, v: Queue]


async def notification_server(reader: StreamReader, writer: StreamWriter):
    """Notification Server which acts as a publisher

    Receives events from trigger service and sends out event to it publishers

    Args:
        reader (StreamReader): Reader stream
        writer (StreamWriter): Writer stream

    Raises:
        CancelledError - When co-routine task is cancelled
        IncompleteReadError - When a client is disconnected pre-maturely
    """
    peer = writer.transport.get_extra_info('peername')
    logger.info('I am connected to %s', peer)

    # Receive Hello message from client
    message = await read_msg(reader)
    client_name, message = message.split()
    logger.info('Received %s from %s', message, client_name)

    # Complete handshake with the client
    if message and message.lower() == 'hello':
        logger.info('Sending hello message back to client.')
        await send_msg(writer, 'hello')

    # Receive Subscriber message from client
    subscribed_state = await read_msg(reader)

    try:
        # Handle Trigger
        if subscribed_state.lower() == 'trigger':
            logger.info('Registering %s', client_name)

            # Create a task to receive state info from trigger
            loop = asyncio.get_event_loop()
            loop.create_task(trigger_task(reader))
        else:
            # Queue up client to subscriber list
            subscriber[subscribed_state].append(writer)

            # Create a task to send state info to client
            loop = asyncio.get_event_loop()
            loop.create_task(send_task(writer, send_queue[writer]))
            logger.info('%s subscribed for %s', client_name, subscribed_state)

            # Create a channel for the subscribed state
            state_queue[subscribed_state] = Queue(25)
            logger.info('Creating channel \'%s\' for %s', subscribed_state, client_name)
            loop.create_task(channel(client_name, subscribed_state))

        # To keep the notification server running
        while True:
            await asyncio.sleep(1.0)

    except asyncio.CancelledError:
        logger.debug('Stopping Co-routine for \'[%s] %s\'', subscribed_state, client_name)
    except asyncio.streams.IncompleteReadError:
        logger.debug('[%s] %s disconnected.', subscribed_state, client_name)
    finally:
        if subscribed_state.lower() != 'trigger':
            del send_queue[writer]
            subscriber[subscribed_state].remove(writer)
        logger.debug('[%s] %s closed.', subscribed_state, client_name)


async def trigger_task(reader):
    """Receive events from trigger and send them to client

    Args:
        reader (StreamReader): Reader stream to read messages from trigger
    """

    while True:
        _rcv = await read_msg(reader)
        if not _rcv:
            continue

        _state, _machine = _rcv.split(' ')
        if is_valid_state(_state) and _state in state_queue:
            await state_queue[_state].put(_machine)


async def send_task(writer, que):
    """Receive data from queue and send this to writer utility

    Args:
        writer (StreamWriter): Writer stream to write the state information
        que (Queue): Send queue

    Raises:
        ConnectionResetError - when client gets disconnected
    """
    _data = None
    try:
        while True:
            _data = await que.get()

            if _data is None:
                writer.write_eof()
                writer.close()
                logger.info('Send task terminated.')
                break
            await send_msg(writer, _data)
    except ConnectionResetError:
        logger.debug('Send task closed.%s', ' Dropped {}'.format(_data) if _data else '')


async def channel(client, state):
    """Receive message from queue and write it to subscription channel

    Args:
        client (str): Client name
        state (str): Subscription State
    """
    while True:
        writers = subscriber[state]
        msg = await state_queue[state].get()

        if msg is None:
            logger.debug('Closing channel %s for %s.', state, client)
            break

        for writer in writers:
            if not send_queue[writer].full():
                logger.info('Sending %s-%s to %s', state, msg, client)
                await send_queue[writer].put(msg)


def is_valid_state(_st) -> bool:
    """Checks if the subscription state received is valid or not.

    Args:
        _st (str): Subscription state

    Returns:
        bool True if received state in subscription list
             False otherwise
    """
    for s in subscriptions:
        if s.lower() == _st.lower():
            return True
    return False


def main(args):
    """Starts the notification server.

    Args:
        args (Namespace): command line arguments

    Raises:
        NotImplementedError - When running on windows operating system
    """
    _loop = asyncio.get_event_loop()
    try:
        # Register exit handlers
        for sig in ('SIGTERM', 'SIGINT'):
            _loop.add_signal_handler(getattr(signal, sig), exit_handler)
    except NotImplementedError:
        logger.info('Signal handling ignored in Windows')
    co_routine = asyncio.start_server(notification_server, host=args.host, port=args.port,
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


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description='''Application which communicates 
    between notification trigger and clients.''')
    cli.add_argument('--host', help='Host IP of the server', default='127.0.0.1')
    cli.add_argument('--port', type=int, help='Port in which server is listening to',
                     default=1200)
    cli.add_argument('-v', '--verbose', action="store_true", help='Enable Verbose mode')
    _args = cli.parse_args()

    # Setup logging
    setup_logging(log_name=os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                                        'log', 'server.log')),
                  default_level=logging.DEBUG if _args.verbose else None)
    logger.info(_args)
    logger.info('Server pid: %s', os.getpid())
    main(_args)
