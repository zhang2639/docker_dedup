# coding:utf-8 
class GracefulKiller():

    def __init__(self, desc, objs):
        self.desc = desc
        self.objs = objs

    def register(self):
        import signal
        signal.signal(signal.SIGINT, self.exit_gracefully)  #终止进程
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        print "GracefulKiller [%s] received signal [%d]" % (self.desc, signum)
        # logger.info("GracefulKiller [%s] received signal [%d]" % (self.desc, signum))
        for obj in self.objs:
            result = getattr(obj, 'finalize')()
        print "GracefulKiller [%s] done" % self.desc
