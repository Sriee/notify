import os
import json
import yaml
import socket
import signal
import asyncio
import logging.config

from asyncio import StreamReader, StreamWriter
from time import sleep

once = True
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


class Config(object):
    def __init__(self):
        _yml_path, self._data = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'config.yml')), {}
        if os.path.exists(_yml_path):
            with open(_yml_path) as yrp:
                self._data = yaml.load(yrp)

        if len(self._data) == 0:
            self._data['server_host'] = self._data.get('server_host', '127.0.0.1')
            self._data['server_port'] = self._data.get('server_port', 1200)
            self._data['client_name'] = self._data.get('client_name', socket.gethostname())
            self._data['client_subscriptions'] = self._data.get('client_subscriptions', ['Error'])
            self._data['subscriptions'] = self._data.get('subscriptions', ['Error'])

    @property
    def server_host(self):
        return self._data['server_host']

    @property
    def server_port(self):
        return self._data['server_port']

    @property
    def client_name(self):
        return self._data['client_name']

    @property
    def client_subscriptions(self):
        return self._data['client_subscriptions']

    @property
    def subscriptions(self):
        return self._data['subscriptions']

    def __contains__(self, key):
        return key in self._data

    def __getitem__(self, item):
        if item in self:
            return self._data[item]
        raise KeyError('%s' % item)


config = Config()


def exit_handler():
    """Exit handler."""
    loop = asyncio.get_event_loop()
    loop.stop()
    loop.remove_signal_handler(signal.SIGTERM)


async def read_msg(reader: StreamReader) -> str:
    """Read message from a socket stream

    Args:
        reader (StreamReader): StreamReader instance

    Returns:
        str - Message from the socket stream
    """
    data = await reader.readline()
    message = data.decode().rstrip()
    return message


async def send_msg(writer: StreamWriter, data: str):
    """Send message across a socket stream

    Args:
        writer (StreamWriter): Stream Writer instance
        data (str): Data to write on the stream
    """
    if not data.endswith('\n'):
        data = data + '\n'
    writer.write(data.encode())
    await writer.drain()


def setup_logging(config_path=os.path.abspath(os.path.join(
                    os.path.dirname(__file__), '..', 'data', 'log_config.json')),
                  default_level=None,
                  log_name=None):
    """Setup logging configuration

    Args:
        config_path (str): Path to log configuration file
        default_level: log level
        log_name (str): Path to log file name
    """
    # Create a log folder
    log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'log'))
    if not os.path.isdir(log_path):
        os.makedirs(log_path)

    path = config_path
    if os.path.exists(path):
        with open(path, 'r') as f:
            lg_config = json.load(f)

        if default_level:
            lg_config['loggers']['main']['level'] = default_level
        else:
            lg_config['loggers']['main']['level'] = logging.INFO

        if log_name:
            lg_config['handlers']['file']['filename'] = log_name

        logging.config.dictConfig(lg_config)
    else:
        logging.basicConfig(level=default_level)
