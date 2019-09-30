
import abc

class ChunkScheduler(object):
    """ Base class for chunk schedulers"""

    __metaclass__ = abc.ABCMeta

    def __init__(self, sites, chunks, chunks_mapping):
        self.sites = sites
        self.chunks = chunks
        self.chunks_mapping = chunks_mapping

    @abc.abstractmethod
    def schedule(self):
        pass
