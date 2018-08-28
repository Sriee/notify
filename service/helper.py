import os
import json
import signal
import asyncio
import logging.config

from asyncio import StreamReader, StreamWriter
from time import sleep

# Configure subscriptions here
subscriptions = ['Pending', 'Imaging', 'Executing', 'Error', 'Completed', 'Suspended']

linux, windows = (None,) * 2

try:
    import pgi as linux

    linux.install_as_gi()
    linux.require_version('Notify', '0.7')
    from pgi.repository import Notify
    Notify.init('Client Notifier')
except ImportError:
    linux, Notify = (None,) * 2

if not linux:
    try:
        import win10toast as windows
    except ImportError:
        windows = None

if linux:
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
            return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data',
                                                'error.ico'))
        elif state == 'suspended':
            return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data',
                                                'warning.ico'))
        else:
            return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data',
                                                'info.ico'))

    def show(title, message):
        toaster = windows.ToastNotifier()
        toaster.show_toast(title, message, icon_path=get_icon(title), duration=5)
else:
    raise NotImplementedError('Notification module not implemented in this OS')

if subscriptions is None or len(subscriptions) == 0:
    raise ValueError('Subscriptions not configured.')

for k in subscriptions:
    if not isinstance(k, str):
        raise TypeError('Expected \'str\' but got \'{}\''.format(type(k)))


def exit_handler():
    loop = asyncio.get_event_loop()
    loop.stop()
    loop.remove_signal_handler(signal.SIGTERM)


async def read_msg(reader: StreamReader) -> str:
    data = await reader.readline()
    message = data.decode().rstrip()
    return message


async def send_msg(writer: StreamWriter, data: str):
    if not data.endswith('\n'):
        data = data + '\n'
    writer.write(data.encode())
    await writer.drain()


def setup_logging(config_path=os.path.abspath(os.path.join(
                    os.path.dirname(__file__), '..', 'data', 'log_config.json')),
                  default_level=None,
                  log_name=None):
    """Setup logging configuration"""
    # Create a log folder
    log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'log'))
    if not os.path.isdir(log_path):
        os.makedirs(log_path)

    path = config_path
    if os.path.exists(path):
        with open(path, 'r') as f:
            config = json.load(f)

        if default_level:
            config['loggers']['main']['level'] = default_level
        else:
            config['loggers']['main']['level'] = logging.INFO

        if log_name:
            config['handlers']['file']['filename'] = log_name

        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
