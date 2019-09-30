# coding:utf-8 
from abc import ABCMeta, abstractmethod

class DataStore(object):
    """ Base class for data store

    Data store is where the chunks are actually stored
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def put(self, key, value):
        #没用，只做占位置
        pass
    @abstractmethod
    def get(self, key):
        pass
    @abstractmethod
    def exists(self, key):
        pass
    @abstractmethod
    def close(self):
        pass
