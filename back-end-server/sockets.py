import socket


class Socket:

    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((host, port))
        self.s.listen()
        self.client_conn = None

    def accept_client(self):
        return self.s.accept()
        #return ClientSocket(conn), addr

    def close(self):
        self.s.close()


class ClientSocket:

    def __init__(self, conn):
        self.conn = conn

    def receive(self, bytes):
        return self.conn.recv(bytes)

    def send(self, data):
        self.conn.sendall(data)

    def close(self):
        self.conn.close()
