import socket
import logging

from .http import HTTPValidator


def receive_HTTP_packet(conn):
    logger = logging.getLogger("SOCKET")
    data = b''
    while not HTTPValidator.is_HTTP_packet(data):
        logger.debug("RECEIVING")
        new_data = conn.recv(1024)
        if new_data == b'':
            return data
        data += new_data
        logger.debug("DATA: %r", data)
    logger.debug("FINAL DATA: %r", data)
    return data


class ClientSocket:

    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))

    def receive(self):
        return receive_HTTP_packet(self.s)

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
        return receive_HTTP_packet(self.conn)

    def send(self, data):
        return self.conn.sendall(data)

    def shutdown(self):
        return self.conn.shutdown(socket.SHUT_RDWR)

    def close(self):
        return self.conn.close()
