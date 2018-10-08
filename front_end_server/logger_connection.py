from threading import Lock

from connectivity.sockets import ServerSocket, LogSenderSocket


class LoggerConnection:

    def __init__(self, host, port):
        self.mutex = Lock()
        self.logger_socket = ServerSocket(host, port)
        conn, addr = self.logger_socket.accept_client()
        self.logger_connection = LogSenderSocket(conn)

    def send_log(self, addr, method, status):
        with self.mutex:
            self.logger_connection.send(addr, method, status)

    def close(self):
        self.logger_socket.close()
        self.logger_connection.close()