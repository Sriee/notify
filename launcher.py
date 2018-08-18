import os
import sys
import subprocess
import shelve
import argparse
import json
import logging.config

from collections import namedtuple
from random import randint

Specification = namedtuple('Specification', 'pid host port subscriptions')
log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'log'))
logger = logging.getLogger('main')


class Client(object):

    def __init__(self, num_clients, name, host, port):
        self._num_of_clients = num_clients
        self._clients = {}
        self._name = name
        self._host = host
        self._port = port
        self._persistent_file_name = '.clients.db'

    @property
    def num_of_clients(self):
        return self._num_of_clients

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def random_state(self) -> list:
        temp, rand_states, = ['Pending', 'Imaging', 'Executing', 'Error', 'Completed',
                              'Suspended'], []
        for i in range(randint(1, 4)):
            idx = randint(0, len(temp) - 1)
            rand_states.append(temp[idx])
            del temp[idx]
        return rand_states

    def start_client(self):
        for i in range(1, self._num_of_clients + 1):
            self.name, subs = 'Client-{}'.format(i), self.random_state
            # process = subprocess.Popen([sys.executable, 'service/client.py', '--name',
            #                             self.name, '--sub'] + subs)
            self._clients[self.name] = Specification('1234', self.host, self.port,
                                                     subs)
            logger.info('%s started', self.name)

    def load_client(self):
        self._clients.clear()
        logger.debug('Cleared existing client storage.')

        _path = os.path.abspath(os.path.join(log_path, self._persistent_file_name))
        with shelve.open(_path) as rdb:
            self._clients = rdb['clients']

        logger.info('Loaded client information.')

    def dump_client(self):
        _path = os.path.abspath(os.path.join(log_path, self._persistent_file_name))

        with shelve.open(_path) as wdb:
            wdb['clients'] = self._clients

        logger.info('Client information stored.')

    def stop_client(self):
        self.load_client()
        n, self._num_of_clients = 0, len(self._clients)

        for k in self._clients:
            res = subprocess.run(['kill', str(self._clients[k].pid)])

            if res.returncode == 0:
                n += 1
                logger.debug('{}: Kill {} [Success]'.format(k, self._clients[k].pid))
            else:
                logger.debug('{}: Kill {} [Failed]'.format(k, self._clients[k].pid))
        return n

    def __repr__(self):
        return 'Client Info:\n\nnumber_of_clients={}\npersistent_file_name={}\n\n' \
               '{}'.\
            format(self.num_of_clients, self._persistent_file_name,
                   '\n'.join(['{}: {}'.format(k, self._clients[k].subscriptions) for k in
                              self._clients]))

    def __str__(self):
        return 'Client(name={}, host={}, port={})'.format(self.name, self.host, self.port)


def setup_logging(default_path='log_config.json', default_level=logging.INFO):
    """Setup logging configuration"""

    if not os.path.isdir(log_path):
        os.makedirs(log_path)

    path = default_path
    if os.path.exists(path):
        with open(path, 'r') as f:
            config = json.load(f)

        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def main(args):
    peers = Client(num_clients=args.n, name=args.name, host=args.host,
                   port=args.port)

    logger.info(peers)
    if args.action == 'start':
        peers.start_client()

        if peers.num_of_clients != args.n:
            logger.debug('Launching all clients failed')
        else:
            logger.debug('Launched clients successfully.')

        peers.dump_client()
    else:
        peers.load_client()
        # n = peers.stop_client()
        # logger.debug('Stopped %s/%s clients successfully.', n, peers.num_of_clients)
        print(repr(peers))


if __name__ == '__main__':
    # Setup logging
    setup_logging(default_path=os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                            'data', 'log_config.json')))

    cli = argparse.ArgumentParser(description='Start / Stop client processes')
    cli.add_argument('-n', help='Number of clients', type=int, default=0)
    cli.add_argument('--host', help='Host IP of the server', default='127.0.0.1')
    cli.add_argument('--port', help='Port in which server is listening to', default=1200)
    cli.add_argument('--name', help='Name of the client')
    cli.add_argument('action', choices=['start', 'stop'], help='Start / Stop clients')

    arg = cli.parse_args()
    logger.debug('Argument Received: %s', arg)
    main(arg)
    logger.debug('Quitting launcher.')
