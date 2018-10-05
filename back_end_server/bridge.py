import logging

from connectivity.sockets import ClientHTTPSocket


class Bridge:

    def __init__(self, host, port):
        self.logger = logging.getLogger("BE-Bridge")
        self.logger.debug("Connecting with FE server")
        self.socket = ClientHTTPSocket(host, port)

    def receive_request(self):
        self.logger.debug("Waiting for request")
        req = self.socket.receive()
        self.logger.debug("Request received: %r", req)
        return req

    def answer_request(self, data):
        self.logger.debug("Sending response %r", data)
        self.socket.send(data)

    def shutdown(self):
        self.logger.debug("Closing bridge")
        self.socket.close()
