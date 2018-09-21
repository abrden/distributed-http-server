import socket


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

    def __init__(self, conn):
        self.conn = conn

    def receive(self, bytes):
        return self.conn.recv(bytes)

    def send(self, data):
        return self.conn.sendall(data)

    def shutdown(self):
        return self.conn.shutdown(socket.SHUT_RDWR)

    def close(self):
        return self.conn.close()
