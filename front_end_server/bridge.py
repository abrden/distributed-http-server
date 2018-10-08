from threading import Lock
import pyhash
import logging
from struct import pack, unpack

from connectivity.sockets import ServerSocket, ServersClientBridgePDUSocket


class BridgePDUDecoder:

    @staticmethod
    def decode(pdu):
        status, method_size, req_id_size, content_size = unpack("!iiii", pdu[:16])
        if content_size > 0:
            method, req_id, content = unpack("!{}s{}s{}s".format(method_size, req_id_size, content_size), pdu[16:])
            return status, method.decode(), req_id.decode(), content.decode()
        else:
            method, req_id = unpack("!{}s{}s".format(method_size, req_id_size), pdu[16:])
            return status, method.decode(), req_id.decode(), None


class BridgePDUEncoder:

    @staticmethod
    def encode(method, uri, req_id, content=None):
        if content is not None:
            msg = pack("!iiii{}s{}s{}s{}s".format(len(method), len(uri), len(req_id), len(content)),
                       len(method), len(uri), len(req_id), len(content), method.encode(), uri.encode(), req_id.encode(), content.encode())
        else:
            msg = pack("!iiii{}s{}s{}s".format(len(method), len(uri), len(req_id)),
                       len(method), len(uri), len(req_id), 0, method.encode(), uri.encode(), req_id.encode())
        return msg


class Bridge:

    def __init__(self, host, port, servers):
        self.host = host
        self.port = port
        self.servers = servers
        self.logger = logging.getLogger("FE-Bridge")
        self.socket = ServerSocket(host, port)
        self.be_conn = []
        self.be_conn_locks = []
        self.hasher = pyhash.super_fast_hash()

        self.logger.info("Connecting with BE servers")
        connections = []
        for i in range(self.servers):
            conn, addr = self.socket.accept_client()
            self.logger.info("Connection accepted %r" % (addr,))
            connections.append((addr, conn))

        connections.sort()
        for client in connections:
            cs = ServersClientBridgePDUSocket(client[1])
            self.be_conn.append(cs)
            self.be_conn_locks.append((Lock(), Lock()))  # First lock to coordinate reading, second for writing

    def where_to(self, path):
        return self.hasher(path) % self.servers

    def send_request(self, path, data):
        be_num = self.where_to(path)
        self.logger.debug("Sending request %r to BE %r", data, be_num)
        conn = self.be_conn[be_num]

        with self.be_conn_locks[be_num][0]:
            self.logger.info("Sending request to BE %r", be_num)
            conn.send(data)
            self.logger.debug("Request sent to BE %r", be_num)

    def wait_for_response(self, be_num):
        self.logger.debug("Waiting for BE %r response", be_num)
        conn = self.be_conn[be_num]
        with self.be_conn_locks[be_num][1]:
            content = conn.receive()

        self.logger.info("Received %r response from BE %r", content, be_num)
        return content

    def shutdown(self):
        self.logger.info("Closing bridge")
        self.socket.close()
        for conn in self.be_conn:
            conn.close()
