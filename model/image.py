# coding:utf-8 
import uuid

class Image(object):
    """ Image base class

    Represent a generic image
    contain the uuid of the image
    """

    def __init__(self, uuid):
        self.uuid = uuid

    def __str__(self):
        return "UUID: [%s] -- %s" % (self.uuid, object.__str__(self))


class ChunksImage(Image):
    """ Represent a chunked image with a list of fingertprints"""

    def __init__(self, uuid, fingerprints):
        super(ChunksImage, self).__init__(uuid)
        self.fingerprints = fingerprints  #list 列表

    def add(self, fingerptint):
        self.fingerprints.append(fingerptint)

    @staticmethod
    def new(uuid):
        return ChunksImage(uuid, list())

    def __str__(self):
        return "UUID: [%s] Hashs(%d): %s" % (self.uuid, len(self.fingerprints), object.__str__(self))
