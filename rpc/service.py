import asyncio
import rpyc
import janus
import threading
from rpyc.utils.server import ThreadedServer
from rpyc.utils.helpers import classpartial


class TriggerService(rpyc.Service):

    def __init__(self, send_jq):
        self._send_jq = send_jq

    def exposed_put(self, **kwargs):
        if kwargs.get('stop', None):
            self._send_jq.sync_q.put(None)
        else:
            self._send_jq.sync_q.put('{} {}'.format(kwargs['state'], kwargs['machine']))


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

    service = classpartial(TriggerService, send_jq=queue)
    t = ThreadedServer(service, port=1600)
    t.daeamon = True
    t.start()
