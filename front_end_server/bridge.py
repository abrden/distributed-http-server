from threading import Lock
import pyhash
import email
import logging

from connectivity.sockets import ServerSocket, ServersClientHTTPSocket


class BridgePDUDecoder:

    @staticmethod
    def decode(response):
        request_text = response.decode()

        request_line, rest = request_text.split('\r\n', 1)
        headers_alone, body = rest.split('\r\n\r\n', 1)
        message = email.message_from_string(headers_alone)
        headers = dict(message.items())

        return headers['Request-Id'], response


class BridgePDUEncoder:

    @staticmethod
    def encode(request, req_id):
        required_header, rest = request.decode().split('\r\n', 1)
        return "{required_header}\r\nRequest-Id: {req_id}\r\n{rest}".format(required_header=required_header, req_id=req_id, rest=rest).encode()


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

        self.logger.debug("Connecting with BE servers")
        connections = []
        for i in range(self.servers):
            conn, addr = self.socket.accept_client()
            self.logger.debug("Connection accepted %r" % (addr,))
            connections.append((addr, conn))

        connections.sort()
        for client in connections:
            cs = ServersClientHTTPSocket(client[1], client[0])
            self.be_conn.append(cs)
            self.be_conn_locks.append((Lock(), Lock()))  # First lock to coordinate reading, second for writing

    def where_to(self, path):
        return self.hasher(path) % self.servers

    def send_request(self, path, data):
        be_num = self.where_to(path)
        self.logger.debug("Sending request %r to %r", data, be_num)
        conn = self.be_conn[be_num]

        with self.be_conn_locks[be_num][0]:
            self.logger.debug("Sending request to %r", be_num)
            conn.send(data)
            self.logger.debug("Request sent to %r", be_num)

    def wait_for_response(self, be_num):
        self.logger.debug("Waiting for %r response", be_num)
        conn = self.be_conn[be_num]
        with self.be_conn_locks[be_num][1]:
            content = conn.receive()

        self.logger.debug("Received %r response from %r", content, be_num)
        return content

    def shutdown(self):
        self.logger.debug("Closing bridge")
        self.socket.close()
        for conn in self.be_conn:
            conn.close()
