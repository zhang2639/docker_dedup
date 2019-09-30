import logging

from networking.custom_message import CustomMessage


class ProxyRPC_stub(object):
    def __init__(self, cfg, storage_callback):
        pass
    def send(self, msg, sender_id):
        pass
    def start_consuming_msgs(self):
        import time
        time.sleep(10)
    def finalize(self):
        pass


class ProxyRPC(object):
    """ Communication with the proxy layer goes here"""

    def __init__(self, cfg, storage_callback):
        self.cfg = cfg
        self.storage_callback = storage_callback
        self.logger = logging.getLogger('network')
        self._setup_rpc()

    def _setup_rpc(self):
        import zmq
        import threading

        self.context = zmq.Context()
        self.send_socket = self.context.socket(zmq.PAIR)
        self.recv_socket = self.context.socket(zmq.PAIR)
        self.send_socket.bind(self.cfg.zmq_comm_to_proxy_endpoint())
        self.recv_socket.bind(self.cfg.zmq_proxy_to_comm_endpoint())
        self.send_message_lock = threading.Lock()

    def send(self, msg, sender_id):
        self.send_message_lock.acquire()
        self.send_socket.send(str((sender_id, msg.tag, len(msg.body))))
        for part in msg.body:
            self.send_socket.send(part)
        self.send_message_lock.release()

    def start_consuming_msgs(self):
        self.logger.info(' [*] Waiting for messages from storage-backend..')
        while True:
            try:
                recv_data = self.recv_socket.recv()
            except Exception as e:
                self.logger.error("zmq socket closed (could be ignored if closed on exit)")
                self.logger.exception(e)
                break
            destination, tag, nb_body_parts = eval(recv_data)
            body = [self.recv_socket.recv() for _ in range(nb_body_parts)]

            msg = CustomMessage(tag, body)
            self.storage_callback(destination, msg)

    def finalize(self):
        self.logger.info("finalize proxy_rpc")
        self.send_socket.close()
        self.recv_socket.close()
        self.context.term()
