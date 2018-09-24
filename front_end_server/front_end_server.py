from threading import Thread
from multiprocessing import Pipe
import logging

logging.basicConfig(level=logging.DEBUG)

from connectivity.http import HTTPRequestDecoder, HTTPResponseDecoder
from connectivity.sockets import ClientsSocket, ServerSocket
from .bridge import Bridge, BridgePDUDecoder, BridgePDUEncoder
from concurrency.pipes import PipeRead, PipeWrite
from .audit_logger import AuditLogger
from .requests_pending import RequestsPending


class RequestReceiverThread(Thread):

    def __init__(self, conn, address, bridge):
        super(RequestReceiverThread, self).__init__()
        self.conn = conn
        self.address = address
        self.bridge = bridge
        self.logger = logging.getLogger("RequestReceiverThread-%r" % (self.address,))

        self.start()

    def run(self):
        conn = ClientsSocket(self.conn, self.address)
        self.logger.debug("Connected client %r at %r", conn, self.address)

        try:
            data = conn.receive()
        except KeyboardInterrupt:
            self.logger.debug("KeyboardInterrupt received. Ending my run")
            return
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

            conn, addr = self.socket.accept_client()

            self.logger.debug("Client connection accepted")
            handler_thread = self.conn_handler(conn, addr, self.bridge)
            self.logger.debug("Started RequestReceiverThread")
            self.handlers.append(handler_thread)

    def shutdown(self):
        self.logger.debug("Closing client socket")
        self.socket.close()

        for thread in self.handlers:
            self.logger.debug('Joining RequestReceiverThread %s', thread.getName())
            thread.join()


class ResponseSenderThread(Thread):

    def __init__(self, bridge, be_num, logs_in):
        super(ResponseSenderThread, self).__init__()
        self.be_num = be_num
        self.bridge = bridge
        self.logs_in = logs_in
        self.logger = logging.getLogger("ResponseSenderThread-%r" % (self.be_num,))

        self.start()

    def run(self):
        while True:
            self.logger.debug("Waiting for BE server %r response", self.be_num)
            try:
                response = self.bridge.wait_for_response(self.be_num)
            except OSError:
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

            self.logger.debug("Sending log to audit")
            self.logs_in.send([conn.address(), data])


class FrontEndServer:

    def __init__(self, host, port, bridge_host, bridge_port, servers):
        self.logger = logging.getLogger("FrontEndServer")
        self.logger.debug("Building bridge with BE")
        self.bridge = Bridge(bridge_host, bridge_port, servers)
        self.logger.debug("Creating HTTP Server")
        self.http_server = HTTPServer(host, port, RequestReceiverThread, self.bridge)

        self.logger.debug("Creating Pipe for audit logs")
        logs_out, logs_in = Pipe(duplex=False)

        self.logs_in_pipe = PipeWrite(logs_in)
        logs_out_pipe = PipeRead(logs_out)

        self.servers = servers
        self.responders = []
        self.logger.debug("Creating ResponseSender Threads")
        for i in range(self.servers):
            responder = ResponseSenderThread(self.bridge, i, self.logs_in_pipe)
            self.responders.append(responder)
        self.logger.debug("Creating AuditLogger Process")
        self.audit_logger = AuditLogger(logs_out_pipe)

        self.logger.debug("Closing logs out pipe fd")
        logs_out.close()

    def start(self):
        try:
            self.http_server.wait_for_connections()
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        self.logger.debug("Shutting down HTTP Server")
        self.http_server.shutdown()
        self.logger.debug("Closing bridge")
        self.bridge.shutdown()
        for i in range(len(self.responders)):
            self.logger.debug("Joining ResponseSenderThread-%r", i)
            self.responders[i].join()
        self.logger.debug("Closing logs in pipe fd")
        self.logs_in_pipe.close()
        self.logger.debug("Joining AuditLogger Process")
        self.audit_logger.join()
