import yaml


class Config(object):
    def __init__(self, f):
        self.data = None
        with open(f) as CFG:
            self.data = yaml.load(CFG.read())

    def __getitem__(self, k):
        return self.data[k]
