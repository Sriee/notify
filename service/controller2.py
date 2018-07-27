import os
import asyncio
import signal
import functools
import logging.config
from asyncio import StreamReader, StreamWriter

logger = logging.getLogger('__main__')


async def echo(reader: StreamReader, writer: StreamWriter):
    try:
        while True:
            data = await reader.readline()
            if data:
                writer.write(data.upper())
                await writer.drain()
    except asyncio.CancelledError:
        logger.debug('Stopping Co-routine')
        writer.write_eof()
    finally:
        writer.close()


def exit_handler(sig):
    logger.debug('Received signal %s' % sig)
    loop = asyncio.get_event_loop()
    loop.stop()
    loop.remove_signal_handler(signal.SIGTERM)


def main():
    _loop = asyncio.get_event_loop()
    _loop.add_signal_handler(getattr(signal, 'SIGTERM'), functools.partial(
        exit_handler, signal.SIGTERM))
    co_routine = asyncio.start_server(echo, '127.0.0.1', 8888, loop=_loop)
    server = _loop.run_until_complete(co_routine)
    try:
        logger.debug('Starting event loop')
        _loop.run_forever()
    finally:
        logger.debug('Event loop terminated.')
        server.close()
        tasks = asyncio.Task.all_tasks()
        group = asyncio.gather(*tasks, return_exceptions=True)
        group.cancel()
        _loop.run_until_complete(group)
        _loop.close()


if __name__ == '__main__':
    # Setup logging
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s:%(levelname)s: %(message)s",
                "datefmt": "[%m-%d-%Y][%I:%M]"
            }
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": os.path.abspath(os.path.join('..', 'controller.log')),
                "maxBytes": 10485760,
                "backupCount": 20,
                "encoding": "utf8"
            }
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["file"]
        }
    }
    )
    logger.debug('pid: %s' % os.getpid())
    main()
