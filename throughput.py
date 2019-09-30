"""Throughput test

original source code:
http://svn.python.org/projects/python/tags/r271/Demo/sockets/throughput.py
"""


import sys, time
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread


DEFAULT_PORT = 50000 + 42
BUFSIZE = 1024*8
# time of the test
TEST_TIME = 5


class ThroughputTestServer(Thread):

    def __init__(self, port=DEFAULT_PORT):
        super(ThroughputTestServer, self).__init__()
        self.setDaemon(True)
        self.port = port

    def run(self):
        s = socket(AF_INET, SOCK_STREAM)
        s.bind(('', self.port))
        s.listen(1)
        print 'Server ready...'
        finish = False
        while not finish:
            conn, (host, remoteport) = s.accept()
            while 1:
                data = conn.recv(BUFSIZE)
                if not data:
                    break
                if data.startswith('KO'):
                    finish = True
                    break
                del data
            conn.send('OK\n')
            conn.close()
            print 'Done with', host, 'port', remoteport


class ThroughputTestClient(object):

    def __init__(self, host, port=DEFAULT_PORT):
        super(ThroughputTestClient, self).__init__()
        self.host = host
        self.port = port

    def finish_server(self):
        s = socket(AF_INET, SOCK_STREAM)
        print 'connect to local server'
        s.connect(('localhost', self.port))
        s.send('KO')
        s.shutdown(1)

    def run(self):
        testdata = 'x' * (BUFSIZE-1) + '\n'
        t1 = time.time()
        s = socket(AF_INET, SOCK_STREAM)
        t2 = time.time()
        print 'connect to host:', (self.host, self.port)
        s.connect((self.host, self.port))
        t3 = time.time()
        count = 0
        while int(time.time()-t3) < TEST_TIME:
            s.send(testdata)
            count += 1
        s.shutdown(1) # Send EOF
        t4 = time.time()
        data = s.recv(BUFSIZE)
        t5 = time.time()
        throughput = round((BUFSIZE * count * 0.001*0.001) / (t5-t1), 3)
        print data
        print 'Msg count:', count
        print 'Raw timers:', t1, t2, t3, t4, t5
        print 'Intervals:', t2-t1, t3-t2, t4-t3, t5-t4
        print 'Total:', t5-t1
        print 'Throughput:', throughput, 'M/sec.'
        return throughput
