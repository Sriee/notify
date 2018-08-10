from asyncio import Queue
from collections import defaultdict, deque
from helper import *

logger = logging.getLogger('main')

subscriber = defaultdict(deque)  # [k: String, v: Deque]
send_queue = defaultdict(Queue)  # [k: Writer, v: Queue]
state_queue = {}                 # [k: String, v: Queue]


async def echo_server(reader: StreamReader, writer: StreamWriter):
    peer = writer.transport.get_extra_info('peername')
    logger.info('I am connected to %s', peer)

    # Receive Hello message from client
    message = await read_msg(reader)
    logger.info('Received %s from client', message)

    client_name, message = message.split()
    # Complete handshake with the client
    if message and message.lower() == 'hello':
        logger.info('Sending hello message back to client.')
        await send_msg(writer, 'hello')

    # Receive Subscriber message from client
    subscribed_state = await read_msg(reader)

    # Handle Trigger
    if subscribed_state.lower() == 'trigger':
        logger.debug('Registering %s', client_name)
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

    try:
        # Receive events from trigger and send them to client
        while True:
            _rcv = await read_msg(reader)
            if not _rcv:
                logger.debug('Received %s from %s', str(_rcv), client_name)
                continue

            _state, _machine = _rcv.split(' ')
            if is_valid_state(_state) and _state in state_queue:
                await state_queue[_state].put(_machine)

    except asyncio.CancelledError:
        logger.debug('Stopping Co-routine for \'[%s] %s\'', subscribed_state, client_name)
    except asyncio.streams.IncompleteReadError:
        logger.debug('[%s] %s disconnected.', subscribed_state, client_name)
    finally:
        if subscribed_state.lower() != 'trigger':
            del send_queue[writer]
            subscriber[subscribed_state].remove(writer)
        logger.debug('[%s] %s closed.', subscribed_state, client_name)


async def send_task(writer, que):
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
    return _st.lower() in ('completed', 'error', 'executing', 'imaging', 'pending', 'suspended')


def main():
    _loop = asyncio.get_event_loop()
    _loop.add_signal_handler(getattr(signal, 'SIGTERM'), exit_handler)
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


if __name__ == '__main__':
    # Setup logging
    setup_logging(log_name=os.path.abspath(os.path.join('log', 'server.log')))
    logger.info('Server pid: %s', os.getpid())
    main()
