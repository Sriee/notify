import os
import sys
import subprocess
import shelve
import argparse
import json
import logging.config

from collections import namedtuple
from random import randint

Specification = namedtuple('Specification', 'pid host port')
logger = logging.getLogger('main')


class Client(object):

    def __init__(self, num_clients):
        self._num_of_clients = int(num_clients)
        self._clients = {}
        self._assigned = set()
        self._persistent_file_name = '.clients.db'

    @property
    def num_of_clients(self):
        return self._num_of_clients

    def start_client(self):
        for i in range(1, self._num_of_clients + 1):
            name, host, port = 'Client-{}'.format(i), '127.0.0.1', self.get_random_port()
            process = subprocess.Popen([sys.executable, 'service/client.py', name, host,
                                        port])

            self._clients[name] = Specification(process.pid, '127.0.0.1', port)
            logger.info('%s started', name)

    def get_random_port(self):
        _port = None

        while not _port:
            _port = randint(1025, 1100)

            if _port in self._assigned:
                _port = None
                continue
            else:
                self._assigned.add(_port)

        return str(_port)

    def load_client(self):
        self._clients.clear()
        logger.debug('Cleared existing client storage.')

        _path = os.path.abspath(os.path.join('log', self._persistent_file_name))
        with shelve.open(_path) as rdb:
            self._clients = rdb['clients']

        logger.info('Loaded client information.')

    def dump_client(self):
        _path = os.path.abspath(os.path.join('log', self._persistent_file_name))

        with shelve.open(_path) as wdb:
            wdb['clients'] = self._clients

        logger.info('Client information stored.')

    def stop_client(self):
        self.load_client()
        self._num_of_clients = len(self._clients)

        for k in self._clients:
            subprocess.run(['kill', str(self._clients[k].pid)])
            logger.debug('{}: Kill {}'.format(k, self._clients[k].pid))

    def __str__(self):
        return 'Client(number_of_clients={}, is_persistent_storage_present={})'\
            .format(self._num_of_clients,
                    os.path.isfile(os.path.abspath(
                        os.path.join('log', self._persistent_file_name))))


def setup_logging(default_path='log_config.json', default_level=logging.INFO):
    """Setup logging configuration"""

    if not os.path.isdir('log'):
        os.makedirs('log')

    path = default_path
    if os.path.exists(path):
        with open(path, 'r') as f:
            config = json.load(f)

        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def main(args):
    peers = Client(args.n)

    if args.action == 'start':
        peers.start_client()

        if peers.num_of_clients != int(args.n):
            logger.debug('Launching all clients failed')
        else:
            logger.debug('Launched clients successfully.')

        peers.dump_client()
    else:
        peers.stop_client()


if __name__ == '__main__':
    # Setup logging
    setup_logging()

    cli = argparse.ArgumentParser(description='Start / Stop client processes')
    cli.add_argument('-n', help='Number of clients', default=0)
    cli.add_argument('action', choices=['start', 'stop'], help='Start / Stop clients.')

    arg = cli.parse_args()
    logger.debug('Argument Received: %s', arg)
    main(arg)
    logger.debug('Quitting launcher.')
