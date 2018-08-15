import asyncio
import rpyc
import threading
from rpyc.utils.server import ThreadedServer
from asyncio import Queue

queue = Queue(25)


class TestService(rpyc.Service):
    def exposed_put(self, state, machine):
        queue.put('{} {}'.format(state, machine))


async def store_it():
    while True:
        _item = await queue.get()

        if not _item:
            break

        with open('temp.txt', 'a') as wp:
            wp.write(_item + '\n')
            wp.flush()


def loop_in_thread(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(store_it())


if __name__ == '__main__':
    _loop = asyncio.get_event_loop()
    athread = threading.Thread(target=loop_in_thread, args=(_loop,))
    athread.start()
    print('Am I blocking..')

    t = ThreadedServer(TestService, port=1500)
    t.daeamon = True
    t.start()
