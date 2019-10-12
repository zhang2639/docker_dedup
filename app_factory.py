class AppFactory(object):
    """ Create all the objects of the system"""

    def __init__(self, cfg):
        self.cfg = cfg
        self.storage = self.wsdriver = self.killer = None

    def build(self):

        from storage.compressor import CompressorFactory
        compressor = CompressorFactory.CreateCompressor(self.cfg.compression_level())

        storage_backend = self.cfg.storage_backend()
        self.cfg.logger.info("storage_backend: %s" % storage_backend)

        if storage_backend == 'redis':
            from db.redisstore import RedisStore
            datastore = RedisStore(self.cfg.storage_address())
        elif storage_backend == 'cassandra':
            image_type = self.cfg.image_type()
            if image_type == 0:
                from db.cassandrastore import CassandraStore
                datastore = CassandraStore(self.cfg.storage_address())
            else:
                from db.cassandrastore import CassandraStore_use_image_type
                datastore = CassandraStore_use_image_type(self.cfg.storage_address())
        else:
            raise Exception('unknown storage backend: [%s]' % storage_backend)


        storage_method = self.cfg.storage_method()
        self.cfg.logger.info("storage_method: %s" % storage_method)

        if storage_method == 'dedup':
            from storage.dal import DAL
            from storage.hasher import xxHasher, Hasher256, MD5
            from storage.dedup_backend import DedupBackendStorage

            chunk_size = self.cfg.chunk_size()
            storage_algorithm = self.cfg.storage_algorithm()
            if storage_algorithm == 'xxhash':
                dal = DAL(datastore, chunk_size, compressor, xxHasher())
            elif storage_algorithm == 'md5':
                dal = DAL(datastore, chunk_size, compressor, MD5())
            elif storage_algorithm == 'sha256':
                dal = DAL(datastore, chunk_size, compressor, Hasher256())
            else:
                raise Exception('unknown storage algorithm : [%s]' % storage_algorithm)
            self.storage = DedupBackendStorage(dal, self.cfg)

        else:
            raise Exception('unknown storage backend: [%s]' % storage_method)

        self.cfg.logger.info("storage backend is ready")

        from storage.backend_storage_ws import WSDriver, BackendStorageWSServer
        ws = BackendStorageWSServer(self.storage)
        self.wsdriver = WSDriver(ws, self.cfg)
        self.wsdriver.configure()

        self.cfg.logger.info("REST ws is ready")

        # from monitoring import Monitoring
        # import os
        # results_file = os.path.join(self.cfg.LOGS_DIR, "sysinfo.csv")
        # self.monitoring = Monitoring(results_file)
        # self.cfg.logger.info("Monitoring is ready")

        from graceful_killer import GracefulKiller
        self.killer = GracefulKiller('proxy', [self.storage, self.wsdriver])
        # self.killer = GracefulKiller('proxy', [self.storage, self.wsdriver, self.monitoring])
        self.killer.register()

        self.cfg.logger.info("Graceful killer is ready")

        self.cfg.logger.info("Objects graph has been built!")

    def start(self):
        # self.monitoring.start()
        self.cfg.logger.info("starting web service..")
        self.wsdriver.start()
        self.cfg.logger.info("web service stopped")
