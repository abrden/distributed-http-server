import threading
import time
import email
import logging

logging.basicConfig(level=logging.DEBUG)

from .sockets import ServerSocket


class HTTPRequestDecoder:

    @staticmethod
    def decode(data):
        request_text = data.decode()

        request_line, rest = request_text.split('\r\n', 1)
        headers_alone, body = rest.split('\r\n\r\n', 1)
        verb, path, version = request_line.split(' ')
        message = email.message_from_string(headers_alone)
        headers = dict(message.items())

        return verb, path, version, headers, body


class HTTPRequestEncoder:

    @staticmethod
    def encode(host, port, verb, path, body=None):
        h = verb + ' ' + path + ' ' + 'HTTP/1.1\r\nHost: ' + host + ':' + str(port) + '\r\n\r\n'
        if body:
            return (h + body).encode()
        return h.encode()


class HTTPResponseDecoder:

    @staticmethod
    def decode_status_code(data):
        return data.decode().split('\r\n', 1)[0].split(' ')[1]


class HTTPResponseEncoder:

    @staticmethod
    def header(code):
        h = ''
        if code == 200:
            h = 'HTTP/1.1 200 OK\r\n'
        elif code == 201:
            h = 'HTTP/1.1 201 Created\r\n'
        elif code == 204:
            h = 'HTTP/1.1 204 No Content\r\n'
        elif code == 400:
            h = 'HTTP/1.1 400 Bad Request\r\n'
        elif code == 404:
            h = 'HTTP/1.1 404 Not Found\r\n'
        elif code == 409:
            h = 'HTTP/1.1 409 Conflict\r\n'
        elif code == 501:
            h = 'HTTP/1.1 501 Not Implemented\r\n'
        else:
            raise RuntimeError('Un recognized status code')  # TODO specific error

        # Optional headers
        current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        h += 'Date: ' + current_date + '\r\n'
        h += 'Server: Distributed-HTTP-Server\r\n'
        h += 'Content-Type: application/json\r\n'
        h += 'Connection: close\r\n\r\n'

        return h.encode()

    @staticmethod
    def encode(code, content=None):
        header = HTTPResponseEncoder.header(code)
        if content:
            return header + content.encode()
        return header


class HTTPServer:

    def __init__(self, host, port, conn_handler):
        self.logger = logging.getLogger("HTTPServer")
        self.socket = ServerSocket(host, port)
        self.conn_handler = conn_handler

    def wait_for_connections(self):
        while True:
            self.logger.debug("Awaiting new connection")
            try:
                conn, addr = self.socket.accept_client()
            except OSError:  # SIGINT received
                return
            self.logger.debug("Connection accepted")
            worker = threading.Thread(target=self.conn_handler.handle, args=(conn, addr))
            worker.setDaemon(True)
            worker.start()
            self.logger.debug("Started worker thread")

    def shutdown(self):
        self.logger.debug("Closing socket")
        self.socket.shutdown()
        self.socket.close()

        main_thread = threading.current_thread()
        for thread in threading.enumerate():
            if thread is main_thread:
                continue
            self.logger.debug('Joining %s', thread.getName())
            thread.join()
