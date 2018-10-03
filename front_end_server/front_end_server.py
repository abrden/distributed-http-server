from threading import Thread
from multiprocessing import Pipe
from multiprocessing.dummy import Pool
import logging

from connectivity.http import HTTPRequestDecoder, HTTPResponseDecoder
from connectivity.sockets import ClientsSocket, ServerSocket
from .bridge import Bridge, BridgePDUDecoder, BridgePDUEncoder
from concurrency.pipes import PipeRead, PipeWrite
from .audit_logger import AuditLogger
from .requests_pending import RequestsPending


class RequestReceiver:

    @staticmethod
    def receive(conn, address, pending, bridge):
        logger = logging.getLogger("RequestReceiver-%r" % (address,))

        conn = ClientsSocket(conn, address)
        logger.debug("Connected client %r at %r", conn, address)

        try:
            data = conn.receive()
        except KeyboardInterrupt:
            logger.debug("KeyboardInterrupt received. Ending my run")
            return
        logger.debug("Received data from client %r", data)

        verb, path, version, headers, body = HTTPRequestDecoder.decode(data)

        logger.debug("Adding client %r to RequestsPending", conn)
        req_id = pending.new_request(conn)
        logger.debug("Adding req_id %r to request", req_id)
        data = BridgePDUEncoder.encode(data, req_id)
        logger.debug("Sending client request through Bridge %r", data)
        bridge.send_request(path, data)
        logger.debug("Client request sent through Bridge")


class HTTPServer:

    def __init__(self, host, port, receivers_num, pending, bridge):
        self.logger = logging.getLogger("HTTPServer")
        self.socket = ServerSocket(host, port)
        self.pending = pending
        self.bridge = bridge
        self.receivers_pool = Pool(receivers_num)

    def wait_for_connections(self):
        while True:
            self.logger.debug("Awaiting new client connection")
            conn, addr = self.socket.accept_client()
            self.logger.debug("Client connection accepted")

            self.receivers_pool.apply_async(RequestReceiver.receive, (conn, addr, self.pending, self.bridge))
            self.logger.debug("Added connection to receiver pool")

    def shutdown(self):
        self.logger.debug("Closing client socket")
        self.socket.close()

        self.logger.debug("Closing receivers pool")
        self.receivers_pool.close()
        self.logger.debug("Joining receivers pool")
        self.receivers_pool.join()


class ResponseSenderThread(Thread):

    def __init__(self, pending, bridge, be_num, logs_in):
        super(ResponseSenderThread, self).__init__()
        self.be_num = be_num
        self.bridge = bridge
        self.pending = pending
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
            conn = self.pending.get_client_from_request(req_id)
            self.logger.debug("Sending data to client %r", data)
            conn.send(data)
            self.logger.debug("Sent data %r to client", data)
            self.pending.request_completed(req_id)
            self.logger.debug("Closing connection with client")
            conn.close()

            self.logger.debug("Sending log to audit")
            self.logs_in.send([conn.address(), data])


class FrontEndServer:

    def __init__(self, host, port, bridge_host, bridge_port, servers, receivers_num):
        self.logger = logging.getLogger("FrontEndServer")
        self.logger.debug("Building bridge with BE")
        self.bridge = Bridge(bridge_host, bridge_port, servers)

        pending = RequestsPending()

        self.logger.debug("Creating HTTP Server")
        self.http_server = HTTPServer(host, port, receivers_num, pending, self.bridge)

        self.logger.debug("Creating Pipe for audit logs")
        logs_out, logs_in = Pipe(duplex=False)

        self.logs_in_pipe = PipeWrite(logs_in)
        logs_out_pipe = PipeRead(logs_out)

        self.servers = servers
        self.responders = []
        self.logger.debug("Creating ResponseSender Threads")
        for i in range(self.servers):
            responder = ResponseSenderThread(pending, self.bridge, i, self.logs_in_pipe)
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
        for i, r in enumerate(self.responders):
            self.logger.debug("Joining ResponseSenderThread-%r", i)
            r.join()
        self.logger.debug("Closing logs in pipe fd")
        self.logs_in_pipe.close()
        self.logger.debug("Joining AuditLogger Process")
        self.audit_logger.join()
