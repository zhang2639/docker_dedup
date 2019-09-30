
from abc import ABCMeta, abstractmethod

class BackendStorage():
    """ Base class for backend storage

    Currently there is just one.
    """

    __metaclass__ = ABCMeta

    def __init__(self, schema, dal):
        self.schema = schema
        self.dal = dal

    @abstractmethod
    def add_image(self, image_file, meta_data):
        pass

    @abstractmethod
    def checkout_image(self, image_uuid, out_file):
        pass

    @abstractmethod
    def is_image_exist(self, image_uuid):
        pass

    @abstractmethod
    def info(self):
        pass

    @abstractmethod
    def reset(self):
        pass
