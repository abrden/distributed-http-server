import logging
from struct import pack, unpack

from connectivity.sockets import ClientBridgePDUSocket


class BridgePDUDecoder:

    @staticmethod
    def decode(pdu):
        method_size, uri_size, req_id_size, content_size = unpack("!iiii", pdu[:16])
        if content_size > 0:
            method, uri, req_id, content = unpack("!{}s{}s{}s{}s".format(method_size, uri_size, req_id_size, content_size), pdu[16:])
            return method.decode(), uri.decode(), req_id.decode(), content.decode()
        else:
            method, uri, req_id = unpack("!{}s{}s{}s".format(method_size, uri_size, req_id_size), pdu[16:])
            return method.decode(), uri.decode(), req_id.decode(), None


class BridgePDUEncoder:

    @staticmethod
    def encode(status, method, req_id, content=None):
        if content is not None:
            msg = pack("!iiii{}s{}s{}s".format(len(method), len(req_id), len(content)),
                       status, len(method), len(req_id), len(content), method.encode(), req_id.encode(), content.encode())
        else:
            msg = pack("!iiii{}s{}s".format(len(method), len(req_id)),
                       status, len(method), len(req_id), 0, method.encode(), req_id.encode())
        return msg


class Bridge:

    def __init__(self, host, port):
        self.logger = logging.getLogger("BE-Bridge")
        self.logger.debug("Connecting with FE server")
        self.socket = ClientBridgePDUSocket(host, port)

    def receive_request(self):
        self.logger.debug("Waiting for BridgePDU")
        return self.socket.receive()

    def answer_request(self, data):
        self.logger.debug("Sending response %r", data)
        self.socket.send(data)

    def shutdown(self):
        self.logger.debug("Closing bridge")
        self.socket.close()
