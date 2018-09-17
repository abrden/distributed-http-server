from threading import Lock
import logging

logging.basicConfig(level=logging.DEBUG)

from http_server.httpserver import HTTPRequestEncoder
from http_server.sockets import ServerSocket, ClientsSocket


class Bridge:

    def __init__(self, host, port, servers):
        self.host = host
        self.port = port
        self.servers = servers
        self.logger = logging.getLogger("FE-Bridge")
        self.socket = ServerSocket(host, port)
        self.be_conn = []
        self.be_conn_locks = []
        self.logger.debug("Connecting with BE servers")
        for i in range(self.servers):
            conn, addr = self.socket.accept_client()  # TODO Van a quedar ordenados distinto en cada arranque
            self.logger.debug("Connection accepted %r" % (addr,))
            cs = ClientsSocket(conn)
            self.be_conn.append(cs)
            self.be_conn_locks.append(Lock())

    def where_to(self, path):
        location = path.split('/')[1:]
        origin = location[0]
        return hash(origin) % self.servers

    def do_request(self, path, verb, body=None):
        be_num = self.where_to(path)
        self.logger.debug("Sending %r request %r to %r", verb, body, be_num)
        conn = self.be_conn[be_num]

        self.be_conn_locks[be_num].acquire()

        conn.send(HTTPRequestEncoder.encode(self.host, self.port, verb, path, body))

        self.logger.debug("Waiting for %r response", be_num)
        content = conn.receive(1024)  # TODO Receive until ???

        self.be_conn_locks[be_num].release()

        self.logger.debug("Received %r response from %r", content, be_num)
        return content

    def shutdown(self):
        self.logger.debug("Closing bridge")
        for conn in self.be_conn:
            conn.close()
        self.socket.shutdown()
        self.socket.close()


