import os
import json
import signal
import asyncio
import logging.config

from asyncio import StreamReader, StreamWriter
from time import sleep

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


def setup_logging(default_path=os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                            '..', 'data',
                                                            'log_config.json')),
                  default_level=None,
                  log_name=None):
    """Setup logging configuration"""

    path = default_path
    if os.path.exists(path):
        with open(path, 'r') as f:
            config = json.load(f)

        config['loggers']['main']['level'] = default_level if default_level else logging.INFO
        if log_name:
            config['handlers']['file']['filename'] = log_name

        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
