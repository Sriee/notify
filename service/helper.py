import os
import asyncio
import json
import signal
import logging.config
from asyncio import StreamReader, StreamWriter


async def exit_handler():
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


def setup_logging(default_path='log_config.json', default_level=logging.INFO,
                  log_name=None):
    """Setup logging configuration"""

    path = default_path
    if os.path.exists(path):
        with open(path, 'r') as f:
            config = json.load(f)

        if log_name:
            config['handlers']['file']['filename'] = log_name

        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
