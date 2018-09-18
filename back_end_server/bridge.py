import logging
logging.basicConfig(level=logging.DEBUG)

from http_server.sockets import ClientSocket


class Bridge:

    def __init__(self, host, port):
        self.logger = logging.getLogger("BE-Bridge")
        self.logger.debug("Connecting with FE server")
        self.socket = ClientSocket(host, port)

    def receive_request(self):
        self.logger.debug("Waiting for request")
        return self.socket.receive(1024)

    def answer_request(self, data):
        self.logger.debug("Sending response %r", data)
        self.socket.send(data)

    def shutdown(self):
        self.logger.debug("Closing bridge")
        self.socket.close()