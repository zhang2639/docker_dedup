import struct
# i in [0..2**32-1], len(ret) == 4
i2b = lambda i: struct.pack("I", i)
b2i = lambda b: struct.unpack("I", b)[0]


class ReadByteException(Exception):
    """Exception raised when socket are closed"""
    def __init__(self, msg):
        super(ReadByteException, self).__init__(msg)
