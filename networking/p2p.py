# coding:utf-8 
import logging
import socket
from threading import Thread

from networking.custom_message import CustomMessage
from networking.mega_socket import MegaSocket
from networking.net_utils import i2b, b2i
from networking.proxy_rpc import ProxyRPC
# from networking.proxy_rpc import ProxyRPC_stub as ProxyRPC


class PeerNode(object):
    """ Main class responsible for networking

    Communicate with the proxy layer and
    maintain connections with other peers
    """

    def __init__(self, cfg):

        self.cfg = cfg
        self.peer_id = self.cfg.peer_id()

        self.max_conn_count = self.cfg.concurrent_conn_count()

        self.logger = logging.getLogger('network')

        self.create_socket = lambda: socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.endpoints = self.cfg.peers()
        self.nb_peers = len(self.endpoints)
        self.peers_ids = range(self.nb_peers)
        self.peer_addr = self.endpoints[self.peer_id]

        self.sockets_lst = [MegaSocket(peer_id, self._notify_message_received)
                            for peer_id in range(self.nb_peers)]
        self.sockets_lst[self.peer_id] = None

        self.logger.info("peer started: ID=%d IP@=%s", self.peer_id, self.peer_addr)

        self._init_sockets()
        self.logger.info("Sockets are ready.")

        sockets_pid = zip(self.peers_ids, self.sockets_lst)
        self.sockets_pid = [u for u in sockets_pid if u[1] is not None]

        self.proxy_rpc = ProxyRPC(self.cfg, self._storage_callback)

        self._start_inspecting_packets()


    def start(self):
        self.logger.info("start")
        # import time
        # time.sleep(5)
        # for k in range(6):
        #     msg = CustomMessage(1, ["%d>> Ola from %d" % (k, self.peer_id)])
        #     self.publish_message(msg)
        self.proxy_rpc.start_consuming_msgs()


    def _listen_for_incomming_conn(self):

        self.serversocket = self.create_socket()
        self.serversocket.bind(self.peer_addr) #bind到自己的地址
        self.serversocket.listen(self.nb_peers) #最大监听数量

        self.logger.info("init_sockets: accept..")
        for _ in range(self.peer_id):
            for _ in range(self.max_conn_count):  #貌似是这个节点和其他每个节点能建立的链接的数量
                clientsocket, address = self.serversocket.accept()
                pid = b2i(clientsocket.recv(4))
                if pid not in self.peers_ids:
                    self.logger.error("Connection received from unknow peer id:[%d]", pid)
                    continue
                self.sockets_lst[pid].add_socket(clientsocket) #把客户端建立的链接socket注册保存起来
                self.logger.info("New connection established with peer id:[%d]", pid)

        self.serversocket.close() #maybe question

    def _init_sockets(self):

        accept_conn_t = Thread(name="AcceptConn", target=self._listen_for_incomming_conn) #自己ID之前等待别人链接
        accept_conn_t.start()

        self.logger.info("init_sockets: connect..")
        for pid in range(self.nb_peers-1, self.peer_id, -1):  #ID之后，自己去连接别人
            for _ in range(self.max_conn_count):
                s = self.create_socket()
                s.settimeout(10)
                established = False
                for i in range(10):
                    self.logger.debug("connecting to peer id:[%d] ... %d", pid, i)
                    try:
                        s.connect(self.endpoints[pid])
                        s.send(i2b(self.peer_id))
                        self.sockets_lst[pid].add_socket(s)
                        self.logger.debug("Connected with peer id:[%d]", pid)
                        established = True
                        break
                    except Exception:
                        import time
                        time.sleep(2)
                if not established:
                    self.logger.error("Cannot connect to peer with id:[%d]", pid)
                else:
                    self.logger.info("connected to peer with id:[%d]", pid)

        accept_conn_t.join()

    def _storage_callback(self, destination, msg):

        self.logger.debug("_storage_callback: dest: %s", str(destination))

        if destination is None:
            _rx = sum(x.get_rx() for x in self.sockets_lst if x is not None)
            _tx = sum(x.get_tx() for x in self.sockets_lst if x is not None)
            self._deliver_msg_to_proxy(CustomMessage(7, [str((_rx, _tx))]), -1)
            return

        if destination == -1:
            self.publish_message(msg)
        else:
            self.send_message(destination, msg)

    def _deliver_msg_to_proxy(self, msg, sender_id):
        self.proxy_rpc.send(msg, sender_id)

    def _notify_message_received(self, msg, sender_id):
        self.logger.debug("_notify_message_received: %s %d", msg, sender_id)
        self._deliver_msg_to_proxy(msg, sender_id)


    def _start_inspecting_packets(self):
        for mega_socket_i in self.sockets_lst:
            if mega_socket_i is not None:
                mega_socket_i.start_listening()
        self.logger.info("sockets are listening..")


    def _send_message_wrapper(self, pid, msg):
        if pid not in self.peers_ids:
            self.logger.error("peer with id=[%d] not fount to send message", pid)
            return False
        self.logger.debug("send message: sending [%s] to %d", msg, pid)
        mega_socket = self.sockets_lst[pid]
        return mega_socket.send_message(msg)

    def publish_message(self, msg):
        self.logger.info("publish_message: %s", msg)
        for pid, _ in self.sockets_pid: #除了自己的其他ID
            self._send_message_wrapper(pid, msg)

    def send_message(self, pid, msg):
        return self._send_message_wrapper(pid, msg)


    def finalize(self):
        try:
            self.logger.info("finalize p2p..")
            self.proxy_rpc.finalize()

            self.logger.info("close mega sockets")
            for mega_socket in self.sockets_lst:
                if mega_socket is not None:
                    mega_socket.close()
                    self.logger.debug("mega socket closed")

            self.logger.info("finalize p2p done")

        except Exception as e:
            self.logger.error("finalize p2p error")
            self.logger.exception(e)
