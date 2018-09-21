import uuid
from threading import Thread
import logging

logging.basicConfig(level=logging.DEBUG)

from http_server.httpserver import HTTPRequestDecoder
from http_server.sockets import ClientsSocket, ServerSocket
from .bridge import Bridge, BridgePDUDecoder, BridgePDUEncoder


class RequestsPending:
    clients = {}

    @staticmethod
    def new_request(client_conn):
        req_id = uuid.uuid4().hex
        RequestsPending.clients[req_id] = client_conn
        return req_id

    @staticmethod
    def get_client_from_request(req_id):
        return RequestsPending.clients[req_id]

    @staticmethod
    def request_completed(req_id):
        del RequestsPending.clients[req_id]


class RequestReceiverThread(Thread):

    def __init__(self, conn, address, bridge):
        super(RequestReceiverThread, self).__init__()
        self.conn = conn
        self.address = address
        self.bridge = bridge
        self.logger = logging.getLogger("RequestReceiverThread-%r" % (self.address,))

        self.daemon = True
        self.start()

    def run(self):
        try:
            conn = ClientsSocket(self.conn)
            self.logger.debug("Connected client %r at %r", conn, self.address)

            data = conn.receive(1024)  # TODO receive up to request ending
            self.logger.debug("Received data from client %r", data)

            verb, path, version, headers, body = HTTPRequestDecoder.decode(data)
            self.logger.debug("Verb %r", verb)
            self.logger.debug("Path %r", path)
            self.logger.debug("Version %r", version)
            self.logger.debug("Headers %r", headers)
            self.logger.debug("Body %r", body)

            self.logger.debug("Adding client %r to RequestsPending", conn)
            req_id = RequestsPending.new_request(conn)
            self.logger.debug("Adding req_id %r to request", req_id)
            data = BridgePDUEncoder.encode(data, req_id)
            self.logger.debug("Sending client request through Bridge %r", data)
            self.bridge.send_request(path, data)
            self.logger.debug("Client request sent through Bridge")

        except:
            self.logger.exception("Problem handling clients request")


class HTTPServer:

    def __init__(self, host, port, conn_handler, bridge):
        self.logger = logging.getLogger("HTTPServer")
        self.socket = ServerSocket(host, port)
        self.conn_handler = conn_handler
        self.bridge = bridge
        self.handlers = []

    def wait_for_connections(self):
        while True:
            self.logger.debug("Awaiting new client connection")
            try:
                conn, addr = self.socket.accept_client()
            except OSError:  # SIGINT received
                return
            self.logger.debug("Client connection accepted")
            handler_thread = self.conn_handler(conn, addr, self.bridge)
            self.logger.debug("Started RequestReceiverThread")
            self.handlers.append(handler_thread)

    def shutdown(self):
        self.logger.debug("Closing client socket")
        self.socket.shutdown()
        self.socket.close()

        for thread in self.handlers:
            self.logger.debug('Joining RequestReceiverThread %s', thread.getName())
            thread.join()


class ResponseSenderThread(Thread):

    def __init__(self, bridge, be_num):
        super(ResponseSenderThread, self).__init__()
        self.be_num = be_num
        self.bridge = bridge
        self.logger = logging.getLogger("ResponseSenderThread-%r" % (self.be_num,))

        self.daemon = True
        self.start()

    def run(self):
        while True:
            self.logger.debug("Waiting for BE server %r response", self.be_num)
            response = self.bridge.wait_for_response(self.be_num)
            if response == b'':
                self.logger.debug("Bridge closed remotely. Ending my run")
                return
            self.logger.debug("Received response from BE server %r: %r", self.be_num, response)
            req_id, data = BridgePDUDecoder.decode(response)
            self.logger.debug("Getting client for request %r", req_id)
            conn = RequestsPending.get_client_from_request(req_id)
            self.logger.debug("Sending data to client %r", data)
            conn.send(data)
            self.logger.debug("Sent data %r to client", data)
            RequestsPending.request_completed(req_id)
            self.logger.debug("Closing connection with client")
            conn.close()


class FrontEndServer:

    def __init__(self, host, port, bridge_host, bridge_port, servers):
        self.logger = logging.getLogger("FrontEndServer")
        self.logger.debug("Building bridge with BE")
        self.bridge = Bridge(bridge_host, bridge_port, servers)
        self.logger.debug("Creating HTTP Server")
        self.http_server = HTTPServer(host, port, RequestReceiverThread, self.bridge)

        self.servers = servers
        self.responders = []
        self.logger.debug("Creating ResponseSenderThreads")
        for i in range(self.servers):
            responder = ResponseSenderThread(self.bridge, i)
            self.responders.append(responder)

    def start(self):
        self.http_server.wait_for_connections()

    def shutdown(self):
        self.http_server.shutdown()
        self.bridge.shutdown()
        for i in range(len(self.responders)):
            self.logger.debug("Joining ResponseSenderThread-%r", i)
            self.responders[i].join()
