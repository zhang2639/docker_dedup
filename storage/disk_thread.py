import logging
from threading import Thread


class DiskThread(Thread):
    """ Write chunks to file from the queue

    In producer/consumer pattern
    It is used to reconstruct the image in parallel
    and as soon as chunks are received.
    """

    def __init__(self, filepath, chunk_size, fp_list, q):
        Thread.__init__(self, name="disk")
        self.filepath = filepath
        self.fp_list = fp_list
        self.chunk_size = chunk_size
        self.q = q
        self.inv_fp_list = dict()

        # f=open(self.filepath, "w")
        # f.truncate(filesize)
        # f.close()

    def run(self):
        # self.logger.info('Starting Listener')
        data = list()
        for i, fp in enumerate(self.fp_list[1]):
            if fp not in self.inv_fp_list:
                self.inv_fp_list[fp] = list()
            self.inv_fp_list[fp].append(i)
            data.append(0)

        f = open(self.filepath, 'wb')
        while True:
            fp, chunk = self.q.get()
            if fp == 'None':
                break
            for i in self.inv_fp_list[fp]:
                # print i
#                f.seek(i * self.chunk_size)
#                f.write(chunk)
                data[i] = chunk
        f.write(''.join(data))
        f.close()

def write_chunk_image(filepath, chunk_size, fp_list, q):
    inv_fp_list = dict()
    data = list()
    for i, fp in enumerate(fp_list(1)):
        if fp not in inv_fp_list:
            inv_fp_list[fp] = list()
        inv_fp_list[fp].append(i)
        data.append(0)

    f = open(filepath, 'wb')
    while True:
        fp, chunk = q.get()
        if fp == 'None':
            break
        print len(inv_fp_list[fp])
        for i in inv_fp_list[fp]:
            data[i] = chunk
        f.write(''.join(data))
        f.close()    
