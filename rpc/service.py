import asyncio
import rpyc
import janus
import threading
from rpyc.utils.server import ThreadedServer


class TestService(rpyc.Service):
    def __init__(self, send_jq):
        self._send_jq = send_jq

    def exposed_put(self, state, machine):
        self._send_jq.sync_q.put('{} {}'.format(state, machine))


async def store_it(jq):
    while True:
        _item = await jq.async_q.get()

        if not _item:
            break

        with open('temp.txt', 'a') as wp:
            wp.write(_item + '\n')
            wp.flush()


def loop_in_thread(loop, que):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(store_it(que))


if __name__ == '__main__':
    worker_loop = asyncio.get_event_loop()
    queue = janus.Queue()

    a_thread = threading.Thread(target=loop_in_thread, args=(worker_loop, queue))
    a_thread.start()

    t = ThreadedServer(TestService, port=1600)
    t.daeamon = True
    t.start()
