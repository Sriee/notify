import os
import signal
import asyncio
import functools
import json
import logging.config

logger = logging.getLogger('main')


class ControllerService(object):

    def __init__(self):
        self._terminate = False
        self._loop = asyncio.get_event_loop()

    def exit_handler(self, sig: str):
        logger.info('Exit Handler called with signal %s.' % sig)
        self.terminate = True
        self._loop.stop()

    async def execute(self):
        reader = asyncio.StreamReader(loop=self._loop)
        line = await reader.readline()
        if line:
            logger.info(line)

    @property
    def terminate(self):
        return self._terminate

    @terminate.setter
    def terminate(self, value):
        try:
            if value is True or value is False:
                self._terminate = value
            else:
                raise ValueError()
        except ValueError:
            logger.info('Illegal argument for terminate flag.')


def setup_logging(default_path='log_config.json',
                  default_level=logging.INFO):
    """Setup logging configuration"""
    path = default_path
    if os.path.exists(path):
        with open(path, 'r') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


if __name__ == '__main__':
    # Setup logging
    setup_logging(default_path=os.path.abspath(os.path.join('..', 'log_config.json')))
    service = ControllerService()

    logger.info('Controller service started')

    loop = asyncio.get_event_loop()
    loop.create_task(service.execute())     # Create co-routine
    # Register exit handler
    loop.add_signal_handler(signal.SIGTERM, functools.partial(service.exit_handler,
                                                              'SIGTERM'))
    try:
        logger.debug('Starting event loop')
        loop.run_forever()
    finally:
        logger.debug('Terminating co-routines')
        tasks = asyncio.Task.all_tasks()
        group = asyncio.gather(*tasks, return_exceptions=True)
        group.cancel()
        loop.run_until_complete(group)
        loop.close()
        logger.debug('Event loop terminated')
