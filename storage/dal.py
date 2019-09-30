# coding:utf-8 
import os
from model.image import ChunksImage
from storage import io

class DAL():
    """ Data Access Layer

    Provide more comprehensive api for DB layer
    """

    def __init__(self, ds, chunk_size, compressor, hasher):
        self.ds = ds
        self.chunk_size = chunk_size
        self.compressor = compressor
        self.hasher = hasher


    def store_image(self, img_data):
        serialized_fp = self.serialize_fingerprints(img_data.fingerprints) #将该image的所有哈希序列化成一串数字，然后和uuid存放起来。 这就是image的元数据
        self.ds.put(img_data.uuid, serialized_fp)
        self.ds.persist()

    def retrieve_image_by_uuid(self, img_uuid):
        serialized_fp = self.ds.get(img_uuid)
        fp = self.deserialize_total_fingerprints(serialized_fp)
        return ChunksImage(img_uuid, fp)


    def add_image(self, img_file):

        delete_after = False

        if img_file.endswith(".tar.gz"):
            import tarfile
            tar = tarfile.open(img_file)
            tar.extractall('/tmp/dataset')
            tar.close()
            img_file = '/tmp/' + img_file[:-7]
            delete_after = True

        if img_file.endswith(".zip"):
            io.decompress_file(img_file, '/tmp/d.raw', self.compressor)
            img_file = '/tmp/d.raw'
            delete_after = True

        img_data = ChunksImage.new()
        img_data.fingerprints.extend(self.read_files_from_dir(img_file, self.chunk_size))  #这个迭代器用的好像有问题
        self.store_image(img_data)

        if delete_after:
            import os
            os.remove(img_file)

        return img_data

    def read_files_from_dir(self, path, block_size):
        # path should not end with '/'; path is diff dir
        if (path[-1] == '/'):
            path = path[:-1]

        list_meta = []
        list_dir = []
        # [file, [fp], file, [fp]...[dir]]
        os.chroot(path)

        for root, dirs, files in os.walk(path):
            #相对路径
            string = root.replace(path, '', 1) + '/'
            if dirs:
                dentry = [string + u for u in dirs]
                list_dir.extend(dentry)
            for f in files:
                #print(root.replace(path, '', 1) + '/' + f) #当前路径下所有非目录子文件
                file = string + f
                img_block_gen = io.read_chunks_from_file(root + '/' + f, block_size)
                list_meta.append(file)
                list_meta.append(self.add_chunks(img_block_gen))

        list_meta.append(list_dir)
        return list_meta


    def _get_chunk_iter(self, fp):
        for digest in fp:
            yield self.get_chunk(digest)

    def checkout_image(self, img_data, out_file):
    #out_file is dir and should not end with '/'
        if (out_file[-1] == '/'):
            out_file = out_file[:-1]
        
        if not os.path.exists(out_file):
            os.mkdir(out_file)

        for dirs in img_data.fingerprints[-1]:
            os.mkdir(out_file + dirs)

        i = 0;    
        for fp in img_data.fingerprints[:-1]:
            i += 1
            if i == 2:
                i = 0
                io.write_chunks_to_file(out_file + file, self._get_chunk_iter(fp))
            else:
                file = fp

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
        list_ser = []
        i = 0
        for fp in fps[:-1]:
            i += 1
            if i == 2: 
                i = 0
                for fpp in fp:
                    assert len(fpp) == self.hasher.get_digest_size()
                list_ser.append(''.join(fp))
            else:
                list_ser.append(fp)

        list_ser.append('|'.join(fps[-1]))
        #return  file:fp:file:fp......:dir|dir|...dir
        return ':'.join(list_ser)

    def deserialize_total_fingerprints(self, ser_fps):
        list_des = []
        list_ori = ser_fps.spilt(':')
        i = 0
        for fp in list_ori[:-1]:
            i += 1
            if i == 2:
                i = 0
                list_des.append(self.deserialize_fingerprints(fp))
            else:
                list_des.append(fp)

        list_des.append(list_ori[-1].spilt('|'))
        #return [file, [fp], file, [fp]....[dir]]
        return list_des


    def deserialize_fingerprints(self, ser_fps):
        n = self.hasher.get_digest_size()
        return [ser_fps[i:i+n] for i in xrange(0, len(ser_fps), n)]