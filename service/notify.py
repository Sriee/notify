import os
from time import sleep
from random import randint

try:
    import pgi

    pgi.install_as_gi()
    pgi.require_version('Notify', '0.7')
    from pgi.repository import Notify
    Notify.init('Client Notifier')
except ImportError:
    pgi, Notify = (None,) * 2

if not pgi:
    try:
        import win10toast as windows
    except ImportError:
        windows = None


if pgi:
    def get_icon(state):
        _state = state.lower()
        if _state == 'error':
            return 'dialog-error'
        elif state == 'suspended':
            return 'dialog-warning'
        else:
            return 'dialog-information'

    def show(title, message):
        notification = Notify.Notification.new(title, message, get_icon(title))
        notification.show()
        sleep(5)
        notification.close()
elif windows:

    def get_icon(state):
        _state = state.lower()
        if _state == 'error':
            return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'error.ico'))
        elif state == 'suspended':
            return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'warning.ico'))
        else:
            return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'info.ico'))

    def show(title, message):
        toaster = windows.ToastNotifier()
        toaster.show_toast(title, message, icon_path=get_icon(title), duration=3)
else:
    raise NotImplementedError('Notification module not implemented in this OS')


def get_random_state_machine():
    state = ['Completed', 'Error', 'Executing', 'Imaging', 'Pending', 'Suspended']
    return state[randint(0, len(state) - 1)], 'HIGH' + str(randint(16, 21))


if __name__ == '__main__':
    for i in range(10):
        show(*get_random_state_machine())
