import yaml
from config import config


class ClashConfig:
    def __init__(self, config_path='clash.yml'):
        self.config_path = config_path
        self.config = self.load_config()
        self.new_config = self.generate_listener_config()

    def load_config(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f)
        return conf

    def generate_listener_config(self):
        new_config = {'listeners': [], 'proxies': self.config['proxies']}
        dns_settings = {
            'enable': True,
            'enhanced-mode': 'fake-ip',
            'fake-ip-range': '198.18.0.1/16',
            'default-nameserver': [
                '114.114.114.114',
                '223.5.5.5',
                '8.8.8.8'
            ],
            'nameserver': [
                'https://doh.pub/dns-query'
            ]
        }

        new_config['dns'] = dns_settings
        for i, proxy in enumerate(self.config['proxies']):
            listener = {
                'name': f'mixed{i}',
                'type': 'mixed',
                'port': config['port_start'] + i,
                'proxy': proxy['name']
            }
            new_config['listeners'].append(listener)
        return new_config

    def get_listeners(self):
        return self.new_config['listeners']

    def save_config(self, new_config, new_config_path='new_clash.yml'):
        with open(new_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(new_config, f, allow_unicode=True)
            print('Config saved')


if __name__ == '__main__':
    config = ClashConfig('clash.yml')
    config.save_config(config.new_config)
