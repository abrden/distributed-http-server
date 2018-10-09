from threading import Thread
from multiprocessing.dummy import Pool
import logging

from connectivity.http import HTTPRequestDecoder, HTTPResponseEncoder
from connectivity.sockets import ServerSocket, ServersClientHTTPSocket
from .bridge import Bridge, BridgePDUDecoder, BridgePDUEncoder
from .requests_pending import RequestsPending
from .logger_connection import LoggerConnection


class RequestReceiver:

    @staticmethod
    def receive(conn, address, pending, bridge):
        logger = logging.getLogger("RequestReceiver-%r" % (address,))

        conn = ServersClientHTTPSocket(conn, address)
        logger.info("Connected client %r", address)

        try:
            data = conn.receive()
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received. Ending my run")
            return
        logger.info("Received request from client %r", data)

        method, uri, version, headers, content = HTTPRequestDecoder.decode(data)

        logger.debug("Adding client %r to RequestsPending", conn)
        req_id = pending.new_request(conn)
        logger.info("Building BPDU with req_id %r", req_id)
        data = BridgePDUEncoder.encode(method, uri, req_id, content)
        logger.debug("Sending client request through Bridge")
        bridge.send_request(uri, data)
        logger.info("Client request sent through Bridge")


class HTTPServer:

    def __init__(self, host, port, receivers_num, pending, bridge):
        self.logger = logging.getLogger("HTTPServer")
        self.socket = ServerSocket(host, port)
        self.pending = pending
        self.bridge = bridge
        self.receivers_pool = Pool(receivers_num)

    def wait_for_connections(self):
        while True:
            self.logger.info("Awaiting new client connection")
            conn, addr = self.socket.accept_client()
            self.logger.info("Client connection accepted")

            self.receivers_pool.apply_async(RequestReceiver.receive, (conn, addr, self.pending, self.bridge))
            self.logger.info("Added connection to receiver pool")

    def shutdown(self):
        self.logger.debug("Closing client socket")
        self.socket.close()

        self.logger.info("Closing receivers pool")
        self.receivers_pool.close()
        self.logger.info("Joining receivers pool")
        self.receivers_pool.join()


class ResponseSenderThread(Thread):

    def __init__(self, pending, bridge, be_num, logs_conn):
        super(ResponseSenderThread, self).__init__()
        self.be_num = be_num
        self.bridge = bridge
        self.pending = pending
        self.logs_conn = logs_conn
        self.logger = logging.getLogger("ResponseSenderThread-%r" % (self.be_num,))

        self.start()

    def run(self):
        while True:
            self.logger.info("Waiting for BE %r response", self.be_num)
            try:
                response = self.bridge.wait_for_response(self.be_num)
            except OSError:
                self.logger.info("Bridge closed remotely. Ending my run")
                return

            self.logger.info("Received response from BE %r: %r", self.be_num, response)
            status, method, req_id, content = BridgePDUDecoder.decode(response)

            self.logger.debug("Getting client for request %r", req_id)
            conn = self.pending.get_client_from_request(req_id)

            data = HTTPResponseEncoder.encode(status, content)
            self.logger.info("Sending response to client %r", data)
            conn.send(data)

            self.pending.request_completed(req_id)

            self.logger.debug("Closing connection with client")
            conn.close()

            self.logger.info("Sending log to audit")
            self.logs_conn.send_log(conn.address(), method, status)


class FrontEndServer:

    def __init__(self, host, port, bridge_host, bridge_port, logger_host, logger_port, servers, receivers_num):
        self.logger = logging.getLogger("FrontEndServer")

        self.logger.info("Creating LoggerConnection")
        self.logger_connection = LoggerConnection(logger_host, logger_port)

        self.logger.info("Building bridge with BE Servers")
        self.bridge = Bridge(bridge_host, bridge_port, servers)

        pending = RequestsPending()

        self.logger.info("Creating HTTP Server")
        self.http_server = HTTPServer(host, port, receivers_num, pending, self.bridge)

        self.servers = servers
        self.responders = []
        self.logger.info("Creating ResponseSender Threads")
        for i in range(self.servers):
            responder = ResponseSenderThread(pending, self.bridge, i, self.logger_connection)
            self.responders.append(responder)

    def start(self):
        try:
            self.http_server.wait_for_connections()
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        self.logger.info("Shutting down HTTP Server")
        self.http_server.shutdown()
        self.logger.info("Closing bridge")
        self.bridge.shutdown()
        for i, r in enumerate(self.responders):
            self.logger.debug("Joining ResponseSenderThread-%r", i)
            r.join()
        self.logger.info("Closing LoggerConnection")
        self.logger_connection.close()
