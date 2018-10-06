import socket
from struct import pack, unpack

from .http import HTTPValidator


class LogReceiverSocket:
    def __init__(self, host, port):
        self.s = ClientSocket(host, port)

    def receive(self):
        b_sizes = self.s.receive(12)
        if b_sizes == b'':
            return None
        addr_size, method_size, status = unpack("!iii", b_sizes)
        b_data = self.s.receive(addr_size + method_size)
        if b_data == b'':
            return None
        addr, method = unpack("!{}s{}s".format(addr_size, method_size), b_data)
        return addr.decode(), method.decode(), status

    def close(self):
        self.s.close()


class LogSenderSocket:
    def __init__(self, conn):
        self.s = ServersClientSocket(conn)

    def send(self, addr, method, status):
        addr = "{}:{}".format(addr[0], addr[1])
        msg = pack("!iii{}s{}s".format(len(addr), len(method)),
                   len(addr), len(method), status, addr.encode(), method.encode())
        self.s.send(msg)

    def close(self):
        self.s.close()


class _BridgePDUSocket:
    def __init__(self, s):
        self.s = s

    def receive(self):
        b_size_BPDU = self.s.receive(4)
        if b_size_BPDU == b'':
            return b_size_BPDU
        size_BPDU = unpack("!i", b_size_BPDU)[0]
        return self.s.receive(size_BPDU)

    def send(self, data):
        msg = pack("!i", len(data)) + data
        self.s.send(msg)

    def close(self):
        self.s.close()


class ClientBridgePDUSocket(_BridgePDUSocket):
    def __init__(self, host, port):
        self.s = ClientSocket(host, port)
        super(ClientBridgePDUSocket, self).__init__(self.s)


class ServersClientBridgePDUSocket(_BridgePDUSocket):
    def __init__(self, conn):
        self.s = ServersClientSocket(conn)
        super(ServersClientBridgePDUSocket, self).__init__(self.s)


class _HTTPSocket:

    def __init__(self, s):
        self.s = s

    def receive(self):
        data = b''
        while not HTTPValidator.is_HTTP_packet(data):
            new_data = self.s.receive(1024)
            if new_data == b'':
                return data
            data += new_data
        return data

    def send(self, data):
        self.s.send(data)

    def close(self):
        self.s.close()


class ServersClientHTTPSocket(_HTTPSocket):
    def __init__(self, conn, addr):
        self.s = ServersClientSocket(conn, addr)
        super(ServersClientHTTPSocket, self).__init__(self.s)

    def address(self):
        return self.s.address()


class ClientHTTPSocket(_HTTPSocket):
    def __init__(self, host, port):
        self.s = ClientSocket(host, port)
        super(ClientHTTPSocket, self).__init__(self.s)


class ServerSocket:

    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((host, port))
        self.s.listen()

    def accept_client(self):
        return self.s.accept()

    def close(self):
        return self.s.close()


class _ClientSocket:

    def __init__(self, s):
        self.s = s

    def receive(self, bytes):
        return self.s.recv(bytes)

    def send(self, data):
        return self.s.sendall(data)

    def close(self):
        return self.s.close()


class ServersClientSocket(_ClientSocket):

    def __init__(self, conn, addr=None):
        super(ServersClientSocket, self).__init__(conn)
        self.addr = addr

    def address(self):
        return self.addr


class ClientSocket(_ClientSocket):

    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        super(ClientSocket, self).__init__(self.s)
