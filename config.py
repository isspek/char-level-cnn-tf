import yaml


class Config(object):
    def __init__(self):
        with open('config.yaml', 'r') as stream:
                self.params = yaml.load(stream)
                print(self.params)