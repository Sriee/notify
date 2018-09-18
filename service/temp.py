import os
import yaml
import socket


class Config(object):
    def __init__(self):
        _yml_path, _data = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'config.yml')), {}
        if os.path.exists(_yml_path):
            with open(_yml_path) as yrp:
                _data = yaml.load(yrp)

        self._host = _data.get('server.host', '127.0.0.1'),
        self._port = _data.get('server.port', 1200),
        self._client_name = _data.get('client.name', socket.gethostname()),
        self._client_subscriptions = _data.get('client.subscriptions', ['Error']),
        self._subscriptions = _data.get('subscriptions', None)

    @property
    def server_host(self):
        return self._host

    @property
    def server_port(self):
        return self._port

    @property
    def client_name(self):
        return self._client_name

    @property
    def client_subscriptions(self):
        return self._client_subscriptions

    @property
    def subscriptions(self):
        return self._subscriptions

    def __get_items(self, item):
        if item == 'server_host':
            return self.server_host
        elif item == 'server_port':
            return self.server_port
        elif item == 'client_name':
            return self.client_name
        elif item == 'client_subscriptions':
            return self.client_subscriptions
        elif item == 'subscriptions':
            return self.subscriptions

    def __contains__(self, key):
        return key in ['server_host', 'server_port', ]

    def __getitem__(self, item):
        if item in self:
            return self.__get_items(item)
        raise KeyError('%s' % item)


if __name__ == '__main__':
    config = Config()
    print(config['server_host'], config['server_port'])
