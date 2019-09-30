from abc import ABCMeta, abstractmethod

class Hasher(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def hash(self, x):
        pass

    @abstractmethod
    def get_digest_size(self):
        pass


import xxhash

class xxHasher(Hasher):

    def __init__(self):
        self.hexdigest_size = int(xxhash.xxh64('x').digestsize * 2)

    def hash(self, x):
        return xxhash.xxh64(x).hexdigest()

    def get_digest_size(self):
        return self.hexdigest_size
