
# https://docs.python.org/2/library/zlib.html
# https://docs.python.org/2/library/codecs.html#python-specific-encodings
# zlib_codec	zip, zlib	Compress the operand using gzip	zlib.compress(), zlib.decompress()

import zlib

class ZlibCompressor():

    def __init__(self, level=6):
        self.level = level

    def compress(self, data):
        return zlib.compress(data, self.level)

    def decompress(self, data):
        return zlib.decompress(data)

    def streaming_compression(self, block_gen):
        compobj = zlib.compressobj(self.level)
        for block in block_gen:
            yield compobj.compress(block)
        yield compobj.flush()

    def streaming_decompression(self, block_gen):
        decompobj = zlib.decompressobj()
        for block in block_gen:
            yield decompobj.decompress(block)
        yield decompobj.flush()


class DummyCompressor:

    def __init__(self):
        self.level = 0
        self.compress = lambda x: x
        self.decompress = lambda x: x
        self.streaming_compression = lambda x: x
        self.streaming_decompression = lambda x: x


class CompressorFactory():

    @staticmethod
    def CreateCompressor(compression_level):
        assert compression_level >= 0 and compression_level < 10
        if compression_level == 0:
            return DummyCompressor()
        else:
            return ZlibCompressor(compression_level)
