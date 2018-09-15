import socket


class Socket:

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


class ClientSocket:

    def __init__(self, conn):
        self.conn = conn

    def receive(self, bytes):
        return self.conn.recv(bytes)

    def send(self, data):
        return self.conn.sendall(data)

    def close(self):
        return self.conn.close()
