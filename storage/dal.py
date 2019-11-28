# coding:utf-8 
import os
from model.image import ChunksImage
from storage import io
from rabin import Rabin, get_file_fingerprints, set_min_block_size, set_max_block_size, set_average_block_size

class DAL():
    """ Data Access Layer

    Provide more comprehensive api for DB layer
    """

    def __init__(self, ds, chunk_min_size, chunk_ave_size, chunk_max_size, compressor, hasher):
        self.ds = ds
        self.compressor = compressor
        self.hasher = hasher
        self.size = 0
        set_min_block_size(chunk_min_size)
        set_average_block_size(chunk_ave_size)
        set_max_block_size(chunk_max_size)


    def store_image(self, img_data):
        serialized_fp = self.serialize_fingerprints(img_data.fingerprints) #将该image的所有哈希序列化成一串数字，然后和uuid存放起来。 这就是image的元数据
        self.ds.put(img_data.uuid, serialized_fp)
        self.ds.persist()

    def retrieve_image_by_uuid(self, img_uuid):
        serialized_fp = self.ds.get(img_uuid)
        fp = self.deserialize_total_fingerprints(serialized_fp)
        return ChunksImage(img_uuid, fp)


    def add_image(self, img_file, uuid):
        import os
        
        self.size = self.size + os.path.getsize(img_file)
        length = get_file_fingerprints(img_file)
        length_list = []
        for i, j, k in length:
            length_list.append(str(j))

        img_block_gen = io.read_chunks_from_file(img_file, length)
        img_data = ChunksImage.new(uuid)
        img_data.fingerprints.append('|'.join(length_list))
        img_data.fingerprints.extend(self.add_chunks(img_block_gen))  #这个迭代器用的好像有问题
        self.store_image(img_data)

        return img_data

    def read_files_from_dir(self, path, block_size):
         # path should not end with '/'
        if (path[-1] == '/'):
            path = path[:-1]

        list_meta = []
        list_dir = []
        # [file, [fp], file, [fp]...[dir]]
        #os.chroot(path)
        for root, dirs, files in os.walk(path):
            string = root.replace(path, '', 1) + '/'
            if dirs:
                dentry = [string + u for u in dirs]
                list_dir.extend(dentry)
            for f in files:
                #print(root.replace(path, '', 1) + '/' + f) #当前路径下所有非目录子文件
                file = string + f
                if os.path.islink(root + '/' + f):
                    continue
                try:
                    with open(root + '/' + f, 'rb', buffering=1024*64) as fin:
                        img_block_gen = io.read_chunks_from_file(fin, block_size)
                        list_meta.append(file)
                        list_meta.append(self.add_chunks(img_block_gen))
                except IOError:
                    print 'open %s error' % (root + '/' + f)
                    continue

        list_meta.append(list_dir)
        return list_meta


    def _get_chunk_iter(self, img_data):
        for digest in img_data.fingerprints[1]:
            yield self.get_chunk(digest)

    def checkout_image(self, img_data, out_file):
        io.write_chunks_to_file(out_file, self._get_chunk_iter(img_data))

    def is_image_exist(self, img_uuid):
        return self.ds.exists(img_uuid)

    def is_chunk_exist(self, fp):
        return self.ds.exists(fp)


    def add_chunk(self, chunk):
        h = self.hasher.hash(chunk)
        if not self.ds.exists(h):  #块哈希不存在
            self.ds.put(h, self.compressor.compress(chunk))  #存进数据库key(哈希) - value(压缩块内容)
        return h

    def add_chunks(self, chunks):
        hashes = map(self.add_chunk, chunks)  #第一个参数 function 以参数序列中的每一个元素调用 function 函数，返回包含每次 function 函数返回值的新列表。
        self.ds.persist()
        return hashes

    def get_chunk(self, fp): #获取数据块
        return self.compressor.decompress(self.get_compressed_chunk(fp))

    def add_compressed_chunk(self, h, comp_chunk):
        if not self.ds.exists(h):
            self.ds.put(h, comp_chunk)
        return h

    def get_compressed_chunk(self, fp):
        return self.ds.get(fp)

    def repo_size(self):
        return self.ds.used_memory()

    def serialize_fingerprints(self, fps):
        #[l1|l2|l3, fp, fp, fp...]
        for fp in fps[1:]:
            assert len(fp) == self.hasher.get_digest_size()
        assert len(fps[0].split('|')) == len(fps[1:])

        return fps[0] + ':' + ''.join(fps[1:])

    def deserialize_total_fingerprints(self, ser_fps):
        list_des = []
        list_ori = ser_fps.split(':')
        list_des.append(list_ori[0].split('|'))
        list_des.append(self.deserialize_fingerprints(list_ori[-1]))        
        #return [[l1, l2, l3...], [fp, fp, fp...]]
        return list_des


    def deserialize_fingerprints(self, ser_fps):
        n = self.hasher.get_digest_size()
        return [ser_fps[i:i+n] for i in xrange(0, len(ser_fps), n)]
