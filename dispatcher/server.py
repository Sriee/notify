import os
import logging.config
from collections import namedtuple

Client = namedtuple('Client', 'name host port')
logger = logging.getLogger('main')

def main():
    pass

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
