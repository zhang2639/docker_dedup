# coding:utf-8 
import logging
import threading

from bitarray import bitarray

from model.image import ChunksImage
from scheduler.network_aware_scheduler import NetworkAwareScheduler
from scheduler.random_scheduler import RandomScheduler
from storage.backend_storage import BackendStorage
from storage.stats import Statistics
from storage.zmq_rpc import ZmqStorageNetworkingRpc
from utils import enum


MSG_TAGS = enum(HASH_AVIL=1, CHUNK_REC=2, NEW_IMG=3, REQ_CHUNK=4)


class DedupBackendStorage(BackendStorage):
    """ Represent the proxy layer

    System logic is implemented here
    Central point and communicate with
    storage layer and network layer
    """

    def __init__(self, dal, cfg):
        BackendStorage.__init__(self, 'deduplication', dal)

        self.cfg = cfg

        self.chunks_mapping = {}

        self.logger = logging.getLogger('proxy')

        #self.stat = Statistics(self, self.cfg.output_csv_path())

        self.logger.info("Initialization done")

    ### private methods

    def _retrieve_chunks(self, fingerprints):
        """ Retrieve chunks from other peers.
            we assume that the chunks are available and reachable.
        """
        self.logger.info("retrieve chunks to pid:%d", self.cfg.peer_id())
        self.logger.info(" -fingerprints: %d", len(fingerprints))

        #self.stat.new_state('flow-st', False)
        chunk_scheduler = None
        if self.cfg.chunk_scheduler() == 'random':
            chunk_scheduler = RandomScheduler(None, fingerprints, self.chunks_mapping)
        else:
            raise Exception('unknown chunk scheduler: [%s]' % chunk_scheduler)
        requests = chunk_scheduler.schedule()
        #self.stat.new_state('flow-nd', False)

        # self.logger.info(" -requests: %r", requests)
        self.logger.info(" -requests: src=%d", self.cfg.peer_id())
        for pid in requests:
            self.logger.info(" -- pid:%d nb:%d", pid, len(requests[pid]))

        self.received_chunks = []
        self.nb_requested_chunks = len(fingerprints)

        for pid in requests:
            if not requests[pid]:
                continue
            ser_fps = self.dal.serialize_fingerprints(requests[pid])

        return self.received_chunks

    def _publish_fingerprints(self, img_data):
        self.logger.info("start _publish_fingerprints")
        ser_fps = self.dal.serialize_fingerprints(img_data.fingerprints)
        #通知自己本地的指纹
        self.logger.info("_publish_fingerprints done")

    # def _all_chunks_available_locally(self, img_data):
    #     for fp in set(img_data.fingerprints):
    #         if not self.dal.is_chunk_exist(fp):
    #             return False
    #     return True

    def _get_chunks_non_available_locally(self, img_data):
        i = 0
        list_fp = []
        for fp in img_data.fingerprints[:-1]:
            i += 1
            if i == 2:
                i = 0
                list_fp.extend(fp)

        return filter(lambda fp: not self.dal.is_chunk_exist(fp), set(list_fp)) #该接收两个参数，第一个为函数，第二个为序列，序列的每个元素作为参数传递给函数进行判，然后返回 True 或 False，最后将返回 True 的元素放到新列表中。
                                                                    #set() 函数创建一个无序不重复元素集
    def _update_loc_map(self, fingerprints, sender_id):
        for fp in fingerprints:
            if fp not in self.chunks_mapping:
                self.chunks_mapping[fp] = bitarray(self.cfg.nb_sites())
                self.chunks_mapping[fp].setall(0)
            self.chunks_mapping[fp][sender_id] = 1
        self.logger.debug("chunks_mapping has been updated: len=%d", len(self.chunks_mapping))

    ### callbacks

#    def chunks_received_callback(self, msg_body, sender_id):
#        fp, chunk = msg_body[0], msg_body[1]
#        self.dal.add_compressed_chunk(fp, chunk)
#        self.received_chunks.append(fp)
#        self.q.put((fp, self.dal.compressor.decompress(chunk)))
#        # self.logger.info("new received chunks from %d ", sender_id)
#        if len(self.received_chunks) % 1000 == 0:
#            self.logger.debug("Received chunks so far: %d chunks", len(self.received_chunks))
#        if len(self.received_chunks) == self.nb_requested_chunks:
#            self.on_chunks_received.set()

#    def hash_available_callback(self, msg_body, sender_id):
#        fingerprints = self.dal.deserialize_fingerprints(msg_body[0])
#        self._update_loc_map(fingerprints, sender_id)

#    def chunks_request_callback_thread(self, msg_body, sender_id):
#        fingerprints = self.dal.deserialize_fingerprints(msg_body[0])
#        for fp in fingerprints:
#            # self.logger.info('chunks_request_callback [%d] ***' % sender_id)
#            chunk = self.dal.get_compressed_chunk(fp)
#            self.p2p_rpc.send_message(MSG_TAGS.CHUNK_REC, [fp, chunk], sender_id)
#        self.logger.info("chunks_request_callback for peer [%d] is done.", sender_id)

#    def chunks_request_callback(self, msg_body, sender_id):
#        threading.Thread(target=self.chunks_request_callback_thread,
#                        args=(msg_body, sender_id)).start()

#    def new_image_callback(self, msg_body, sender_id):
#        uuid, ser_fps = msg_body[0], msg_body[1]
#        fingerprints = self.dal.deserialize_fingerprints(ser_fps)
#        self.logger.info("New Image added: uuid=[%s] hashes size=[%dB]", uuid, len(ser_fps))
#        img_data = ChunksImage(uuid, fingerprints)
#        self.logger.info("New Image added: %s", str(img_data))
#        self.dal.store_image(img_data)
#        self._update_loc_map(set(img_data.fingerprints), sender_id)


    ### Public API

    def add_image(self, image_file, image_metadata):
        self.logger.info("DedupBackendStorage: Add Image %s", image_file)
        img_data = self.dal.add_image(image_file)
        # synchronous meta-data replication
        # synchronous meta-data transfer to network module but not other peers!!
        # threading.Thread(target=self._publish_fingerprints, args=(img_data,)).run()
        self._publish_fingerprints(img_data)
        self.logger.info("Image [%s] metadata has been replicated to all sites.", img_data.uuid)
        return img_data.uuid


    def fill_q_with_available_chunks(self, fp_list):
        for fp in fp_list:
            self.q.put((fp, self.dal.get_chunk(fp)))

    def checkout_image(self, image_uuid, out_file):
        self.logger.info("DedupBackendStorage: Checkout Image %s", image_uuid)

        if not self.is_image_exist(image_uuid):
            self.logger.error("Image with UUID [%s] not found.", image_uuid)
            return False
            # raise Exception('Image with UUID [%s] not found.' % image_uuid)

        #self.stat.start(image_uuid)
        #self.stat.new_state('st')

        img_data = self.dal.retrieve_image_by_uuid(image_uuid)
        self.logger.info("Checkout Image %s", str(img_data))
        non_available_fp = self._get_chunks_non_available_locally(img_data)
        if non_available_fp:

            multiprocessing = False
            if multiprocessing: # multiprocessing
                from storage.disk_thread import write_chunk_image
                import multiprocessing as mp
                #must use Manager queue here, or will not work
                #Manager()返回的manager对象控制了一个server进程，此进程包含的python对象可以被其他的进程通过proxies来访问。从而达到多进程间数据通信且安全。
                self.manager = mp.Manager()
                self.q = self.manager.Queue()
                self.pool = mp.Pool(1)
                #put listener to work first
                self.watcher = self.pool.apply_async(
                    write_chunk_image,
                    (out_file, self.cfg.chunk_size(), img_data.fingerprints, self.q))
            else:
                from storage.disk_thread import DiskThread
                from Queue import Queue
                self.q = Queue()
                self.dt = DiskThread(out_file, self.cfg.chunk_size(),
                                     img_data.fingerprints, self.q)
                self.dt.start()

            available_fp = set(img_data.fingerprints) - set(non_available_fp)
            read_local_chunks_t = threading.Thread(
                target=self.fill_q_with_available_chunks, args=(available_fp,))
            read_local_chunks_t.start()

            self.logger.info("Image with uuid=[%s] is not available locally.", image_uuid)

            self.stat.nb_chunks = len(img_data.fingerprints)
            self.stat.nb_uniq_chunks = len(set(img_data.fingerprints))
            self.stat.nb_missing_chunks = len(non_available_fp)
            self.stat.nb_already_available_chunks = \
            self.stat.nb_uniq_chunks - self.stat.nb_missing_chunks

            self.logger.info("%d chunks are missing, out of %d",
                             self.stat.nb_missing_chunks, self.stat.nb_uniq_chunks)

            self.stat.new_state('pull-st')
            hashes = self._retrieve_chunks(non_available_fp)
            self.stat.new_state('pull-nd')
            self.logger.info("All chunks of Image [%s] are available locally now.", image_uuid)
            ser_fps = self.dal.serialize_fingerprints(hashes)
            self.p2p_rpc.send_message(MSG_TAGS.HASH_AVIL, [ser_fps])
            self.logger.info("newly received fingerprints are published.")

            read_local_chunks_t.join()
            self.q.put(('None', 'None'))

            # multiprocessing
            if multiprocessing:
                self.pool.close()
            else:
                self.dt.join()

            #self.stat.new_state('write-st', False)
            #self.stat.new_state('write-nd', False)
        else:
            #self.stat.new_state('pull-st')
            #self.stat.new_state('pull-nd')

            self.logger.info("Start rebuilding Image [%s]..", image_uuid)
            #self.stat.new_state('write-st', False)
            self.dal.checkout_image(img_data, out_file)
            #self.stat.new_state('write-nd', False)

        #self.stat.new_state('nd')
        #self.stat.output_stats()
        self.logger.info("Checkout Image [%s] done.", image_uuid)

        return True

    def is_image_exist(self, image_uuid):
        return self.dal.is_image_exist(image_uuid)

    def measure_network_throughput(self):

        from throughput import ThroughputTestClient
        peers_ip = [x[0] for x in self.cfg.peers()]
        throughput = [ThroughputTestClient(host).run()
                      if idx != self.cfg.peer_id() else 0
                      for idx, host in enumerate(peers_ip)]
        self.peers_affinity = [int(8*t / 25.0 + 0.5) for t in throughput]
        print self.peers_affinity
        print throughput
        return str(throughput) + str(self.peers_affinity)

    def info(self):
        return 'Dump db:\n%s\nDump peers fp size:\n%d' % \
                (self.dal.ds.dump(), len(self.chunks_mapping))

    def reset(self):
        self.logger.info("begin resetting..")
        self.chunks_mapping = dict()
        self.dal.ds.reset()
        self.logger.info("==================================")

    def finalize(self):
        self.logger.info("DedupBackendStorage finalize")
        self.logger.info("DedupBackendStorage finalize done")