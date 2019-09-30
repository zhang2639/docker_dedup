import logging
import socket

from Queue import Queue
from itertools import cycle
from threading import Thread

from networking.connection_listener import ConnectionListener
from networking.net_utils import i2b


class SocketQ(object):
    def __init__(self, s, q, _id):
        self.s = s
        self.q = q
        self._id = _id
        self.tx = 0
        self.t = None

class MegaSocket(object):
    """ Wrapper around TCP socket

    Manage mutiple connections and provide the interface
    for single connection
    """

    def __init__(self, peer_id, callback):
        super(MegaSocket, self).__init__()
        self.peer_id = peer_id
        self.callback = callback
        self.rx = 0
        self._sockets_q = list()
        self.connListeners = list()
        self.logger = logging.getLogger('network')

    def get_rx(self):
        return self.rx
    def get_tx(self):
        return sum(sq.tx for sq in self._sockets_q)

    # def _send_packet_part(self, s, msg_part):
    #     size = len(msg_part)
    #     s.send(i2b(size))
    #     i, bs = 0, 1024
    #     total_written = 0
    #     while i < size:
    #         total_written += s.send(msg_part[i:min(i+bs, size)])
    #         i += bs
    #     assert total_written == size
    #
    # def _send_message_to_socket(self, sq, msg):
    #     self.logger.debug('send msg [%s] thru socket id: %d' % (msg, sq._id))
    #     try:
    #         sq.s.send(chr(msg.tag))
    #         nb_parts = len(msg.body)
    #         sq.s.send(chr(nb_parts))
    #         for part in msg.body:
    #             self._send_packet_part(sq.s, part)
    #         self.tx += 1 + 1 + 4*nb_parts + sum(map(len, msg.body))
    #         return True
    #     except socket.error as e:
    #         self.logger.error('send_packet: socket fails when sending [%s] thru socket id:'
    #          % (msg, sq._id))
    #         return False

    def mysend(self, sock, msg):
        totalsent = 0
        msg_len = len(msg)
        while totalsent < msg_len:
            sent = sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
        return totalsent

    def _send_message_to_socket(self, sq, msg):
        self.logger.debug("send msg [%s] thru socket id: %d", msg, sq._id)
        try:
            nb_parts = len(msg.body)
            packet = chr(msg.tag) + chr(nb_parts) + ''.join([i2b(len(part)) + part for part in msg.body])
            # total_written = sq.s.send(packet)
            total_written = self.mysend(sq.s, packet)
            if total_written != len(packet):
                self.logger.error("total_written(%d) != size(%d)",
                                  total_written, len(packet))
            # self.logger.info('total_written(%d)=%d' % (sq._id, total_written))
            sq.tx += len(packet)
            return True
        except socket.error as e:
            self.logger.error("send_packet: socket fails when sending [%s] "
                              "thru socket id: %d", msg, sq._id)
            return False

    def add_socket(self, _socket):
        sq = SocketQ(_socket, Queue(), len(self._sockets_q))
        self._sockets_q.append(sq)
        conn_listener = ConnectionListener(sq)
        # conn_listener.setDaemon(True)
        self.connListeners.append(conn_listener)

    def send_message(self, msg):
        sq = self.send_pool.next()
        self._send_message_to_socket(sq, msg)
        return True

    def register_callback(self, callback):
        self.callback = callback

    def mega_listener(self):
        for sq in cycle(self._sockets_q):
            msg, rx = sq.q.get(True)
            self.rx += rx
            self.callback(msg, self.peer_id)

    def start_listening(self):

        self.logger.info("start listening: nb sockets: %d", len(self._sockets_q))

        self.send_pool = cycle(self._sockets_q)

        for conn_listener in self.connListeners:
            conn_listener.start()

        t = Thread(name="MegaListener", target=self.mega_listener)
        t.setDaemon(True)
        t.start()

    def close(self):
        for sq in self._sockets_q:
            self.logger.info("tx for socket[%d] = %d", sq._id, sq.tx)
            if not sq.q.empty():
                self.logger.warning("queue is not empty! size=%d", sq.q.qsize())
            # sq.q.join()
            sq.s.close()
