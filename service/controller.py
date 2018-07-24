import os
import signal
from threading import Lock

mutex = Lock()

class ControllerService(object):

    def __init__(self):
        self._terminate = False
        # Exit Handler
        signal.signal(signal.SIGTERM, self.exit_handler)

    def exit_handler(self, sig, func=None):
        print('Exit Handler called.')
        self.terminate = True

    def execute(self):
        pass

    @property
    def terminate(self):
        return self._terminate

    @terminate.setter
    def terminate(self, value):
        mutex.acquire()
        if value is True or value is False:
            self._terminate = value
        else:
            raise ValueError('Illegal argument for terminate flag.')
        mutex.release()



if __name__ == '__main__':
    # Setup logging

    service = ControllerService()

    while not service.terminate:
        service.execute()
