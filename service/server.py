from asyncio import Queue
from contextlib import suppress
from collections import defaultdict, deque
from random import randint
from helper import *

logger = logging.getLogger('main')

subscriber = defaultdict(deque)     # [k: String, v: Deque]
send_queue = defaultdict(Queue)     # [k: Writer, v: Queue]
state_queue = {}                    # [k: String, v: Queue]


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

    # Queue up client to subscriber list
    subscriber[subscribed_state].append(writer)

    # Create a task to send state info to client
    loop = asyncio.get_event_loop()
    send_msg_task = loop.create_task(send_task(writer, send_queue[writer]))
    logger.info('%s subscribed for %s', client_name, subscribed_state)
    # Start sending events to client
    try:
        while True:
            state, machine = get_random_server_state()
            await asyncio.sleep(5)
            # Create a task for each state
            if state not in state_queue:
                state_queue[state] = Queue(25)
                loop.create_task(channel(client_name, state))

            await state_queue[state].put(machine)
    except asyncio.CancelledError:
        logger.debug('Stopping Co-routine')
    except asyncio.streams.IncompleteReadError:
        logger.debug('%s disconnected.', client_name)
    finally:
        logger.debug('%s closed.', client_name)
        send_queue[writer].put(None)
        await send_msg_task
        del send_queue[writer]
        subscriber[subscribed_state].remove(writer)


async def send_task(writer, que):
    while True:
        with suppress(asyncio.CancelledError):
            _data = await que.get()
            if _data is None:
                writer.write_eof()
                writer.close()
                break
            await send_msg(writer, _data)


async def channel(client, state):
    while True:
        writers = subscriber[state]
        if not writers:
            await asyncio.sleep(1)
            continue

        msg = await state_queue[state].get()

        if not msg:
            break

        for writer in writers:
            if not send_queue[writer].full():
                logger.info('Sending %s-%s to %s', state, msg, client)
                await send_queue[state].put(msg)


def get_random_server_state():
    state = ['Error', 'Suspended', 'Pending']
    return state[randint(0, len(state) - 1)], 'HIGH' + str(randint(10, 18))


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
