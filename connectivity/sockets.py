import socket

from .http import receive_HTTP_packet


class ClientSocket:

    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))

    def receive(self):
        return receive_HTTP_packet(self.s)

    def send(self, data):
        return self.s.sendall(data)

    def close(self):
        return self.s.close()


class ServerSocket:

    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((host, port))
        self.s.listen()

    def accept_client(self):
        return self.s.accept()

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

    def close(self):
        return self.conn.close()
