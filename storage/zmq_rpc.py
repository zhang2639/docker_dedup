import logging
import threading

import zmq


class ZmqStorageNetworkingRpc(object):
    """ Communication with the network layer goes here"""

    def __init__(self, cfg):
        self.cfg = cfg
        self.logger = logging.getLogger('proxy')
        self._setup_rpc()

    def _setup_rpc(self):

        self.context = zmq.Context()
        self.send_socket = self.context.socket(zmq.PAIR)
        self.recv_socket = self.context.socket(zmq.PAIR)
        self.recv_socket.setsockopt(zmq.RCVTIMEO, 1000)
        self.recv_socket.connect(self.cfg.zmq_comm_to_proxy_endpoint())
        self.send_socket.connect(self.cfg.zmq_proxy_to_comm_endpoint())
        self.send_message_lock = threading.Lock()
        self.tags_callback = {}

        self.exited = False

        self.listen_thread = threading.Thread(target=self.listen_for_incoming_messages)
        self.listen_thread.start()

    def add_callback(self, tag, callback_func):

        self.tags_callback[tag] = callback_func

    def send_message(self, tag, body, destination=-1):

        header = str((destination, tag, len(body)))

        self.send_message_lock.acquire()
        self.send_socket.send(header)
        for body_part in body:
            self.send_socket.send(body_part)
        self.send_message_lock.release()

    def listen_for_incoming_messages(self):

        self.logger.info(' [*] Waiting for messages from networking layer..')
        while True:
            try:
                recv_data = self.recv_socket.recv()
            except zmq.error.Again as e:
                if self.exited:
                    print "exited = 1"
                    # self.recv_socket.close()
                    return
                # timeout
                continue

            sender_id, tag, nb_body_parts = eval(recv_data)
            body = [self.recv_socket.recv() for _ in range(nb_body_parts)]

            self._callback(tag, body, sender_id)

    def _callback(self, tag, body, sender_id):

        self.tags_callback[tag](body, sender_id)

    def finalize(self):
        self.exited = True
        self.listen_thread.join()
        self.recv_socket.close()
        self.send_socket.close()
        self.context.term()
