import rpyc
from rpyc.utils.server import ThreadedServer


class TestService(rpyc.Service):

    def __init__(self):
        self._rp = None
        self._file = 'temp.txt'

    def on_connect(self, conn):
        self._rp = open(self._file, 'a')
        print('Opened File pointer.')

    def on_disconnect(self, conn):
        self._rp.close()
        print('Closed file pointer.')

    def exposed_put(self, data):
        self.store_it(data)

    def store_it(self, data):
        self._rp.write(data + '\n')


if __name__ == '__main__':
    t = ThreadedServer(TestService, port=1500)
    t.daeamon = True
    t.start()
