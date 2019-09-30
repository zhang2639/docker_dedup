import logging
import socket
from threading import Thread

from networking.custom_message import CustomMessage
from networking.net_utils import b2i, ReadByteException


class ConnectionListener(Thread):
    """ TCP connection listerner

    Parse the received messag
    """

    RECV_BUFFER_SIZE = 8192

    def __init__(self, socket_q):
        Thread.__init__(self, name="CL [%d]" % socket_q._id)
        self.setDaemon(True)
        self.notify = socket_q.q.put
        self.cs = socket_q.s
        self.cs.settimeout(None)
        self.logger = logging.getLogger('network')

    def _recv(self, count):
        try:
            parts = []
            nb_recv_bytes = 0
            while nb_recv_bytes != count:
                data = self.cs.recv(min(ConnectionListener.RECV_BUFFER_SIZE,
                                        count - nb_recv_bytes))
                if not data:
                    print " break"
                    break
                nb_recv_bytes += len(data)
                parts.append(data)
            data = ''.join(parts)
            if count != len(data):
                raise ReadByteException("Attempt to read %d byte, but %d are read"
                                        % (count, len(data)))
            return data
        except socket.timeout:
            print "timeout in _recv"

    def _read_byte(self):
        return ord(self._recv(1))

    def _read_int(self):
        return b2i(self._recv(4))

    def _recv_part(self):
        part_size = self._read_int()
        assert part_size > 0

        parts = []
        nb_recv_bytes = 0
        while nb_recv_bytes != part_size:
            data = self._recv(min(2048, part_size - nb_recv_bytes))
            if not data:
                break
            nb_recv_bytes += len(data)
            parts.append(data)

        if nb_recv_bytes != part_size:
            err_msg = ("ConnectionListener: WRONG part size: "
                       "length [%d/%d]", nb_recv_bytes, part_size)
            self.logger.error(err_msg)
            raise Exception(err_msg)

        return ''.join(parts)

    def run(self):
        self.logger.info("Starting Listener")
        while True:
            try:
                tag = self._read_byte()
                nb_parts = self._read_byte()
                packet_parts = [self._recv_part() for _ in range(nb_parts)]

                msg = CustomMessage(tag, packet_parts)
                self.logger.debug("packet received %s", msg)

                rx = 1 + 1 + 4*nb_parts + sum(map(len, msg.body))
                self.notify((msg, rx))

            except socket.timeout:
                self.logger.debug("socket timeout, but ignored")
            except socket.error as e:
                self.logger.error("run:: socket.error !!!")
                self.logger.exception(e)
                raise e
            except ReadByteException as e:
                self.logger.error("_read_byte error (could be ignored if closed on exit)")
                self.logger.exception(e)
                break
