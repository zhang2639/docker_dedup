# coding:utf-8 
import cherrypy

class BackendStorageWSServer(object):
    """ Expose REST api for the system (i.e. proxy layer)
    """

    def __init__(self, storage):
        self.storage = storage

    @cherrypy.expose
    def add(self, path, image_metadata=None):
        uuid = self.storage.add_image(path, image_metadata)
        return uuid

    @cherrypy.expose
    def checkout(self, uuid, path):
        ok = self.storage.checkout_image(str(uuid), path)
        return str(ok)

    @cherrypy.expose
    def is_available(self, uuid):
        return self.storage.is_image_exist(str(uuid))

    @cherrypy.expose
    def network(self):
        return self.storage.measure_network_throughput()

    @cherrypy.expose
    def reset(self):
        self.storage.reset()
        return 'Reset done.'

    @cherrypy.expose
    def info(self):
        return self.storage.info()


class WSDriver(object):

    def __init__(self, ws, cfg):
        self.ws = ws
        self.cfg = cfg
        self.exited = False

    def configure(self):
        cherrypy.config.update({'server.socket_host': self.cfg.ws_address_bind()})
        #cherrypy.config.update({'server.socket_port': 5000})
        # http://docs.cherrypy.org/en/latest/advanced.html#response-timeouts
        cherrypy.config.update({'response.timeout': 30 * 60})
        cherrypy.config.update({'engine.autoreload.on': False})
        #cherrypy.engine.timeout_monitor.unsubscribe()
        #cherrypy.engine.signals.subscribe()
        cherrypy.config.update({'environment': 'embedded'})

    def start(self):
        try:
            cherrypy.quickstart(self.ws)   #web 框架
        except Exception as e:
            if not self.exited:
                raise e

    def finalize(self):
        self.exited = True
        cherrypy.engine.stop()
        cherrypy.engine.exit()
