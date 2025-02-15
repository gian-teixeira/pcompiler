class DefaultDict(dict):
    def __init__(self, default_factory):
        self.default_factory = default_factory

    def __missing__(self, key):
        self[key] = self.default_factory(key)
        return self[key]
