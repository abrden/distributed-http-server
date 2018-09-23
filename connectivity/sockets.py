import socket
import logging

from .http import HTTPValidator


class ClientSocket:

    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))

    def receive(self, bytes):
        return self.s.recv(bytes)

    def send(self, data):
        return self.s.sendall(data)

    def shutdown(self):
        return self.s.shutdown(socket.SHUT_RDWR)

    def close(self):
        return self.s.close()


class ServerSocket:

    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((host, port))
        self.s.listen()

    def accept_client(self):
        return self.s.accept()

    def shutdown(self):
        return self.s.shutdown(socket.SHUT_RDWR)

    def close(self):
        return self.s.close()


class ClientsSocket:

    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr

    def address(self):
        return self.addr

    def receive(self):
        logger = logging.getLogger("SOCKET")
        data = b''
        while not HTTPValidator.is_HTTP_packet(data):
            logger.debug("RECEIVING")
            data += self.conn.recv(1024)
            logger.debug("DATA: %r", data)
        logger.debug("FINAL DATA: %r", data)
        return data

    def send(self, data):
        return self.conn.sendall(data)

    def shutdown(self):
        return self.conn.shutdown(socket.SHUT_RDWR)

    def close(self):
        return self.conn.close()
