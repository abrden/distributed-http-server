import threading
import time
import logging

logging.basicConfig(level=logging.DEBUG)

from sockets import Socket, ClientSocket


def handle_client_connection(conn, address):
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("Worker-%r" % (address,))

    try:
        conn = ClientSocket(conn)

        logger.debug("Connected %r at %r", conn, address)

        data = conn.receive(1024)  # receive data from client
        logger.debug("Received data %r", data)

        string = bytes.decode(data)  # decode it to string

        request_method = string.split(' ')[0]

        response_headers = HTTPResponseMaker.response(404)
        response_content = b"<html><body><p>Error 404: File not found</p><p>Python HTTP server</p></body></html>"

        server_response = response_headers.encode()  # return headers for GET and HEAD
        server_response += response_content  # return additional conten for GET only

        conn.send(server_response)
        logger.debug("Sent data %r", server_response)
    except:
        logger.exception("Problem handling request")
    finally:
        logger.debug("Closing connection with client")
        conn.close()


class HTTPResponseMaker:

    @staticmethod
    def response(code):
        h = ''
        if (code == 200):
            h = 'HTTP/1.1 200 OK\r\n'
        elif (code == 404):
            h = 'HTTP/1.1 404 Not Found\r\n'

        # Optional headers
        current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        h += 'Date: ' + current_date + '\r\n'
        h += 'Server: BE-HTTP-Server\r\n'
        h += 'Content-Type: application/json\r\n'
        h += 'Connection: close\r\n\r\n'  # signal that the conection wil be closed after complting the request

        return h


class HTTPServer:

    def __init__(self, host, port):
        self.logger = logging.getLogger("BEHTTPServer")
        self.socket = Socket(host, port)

    def wait_for_connections(self):
        while True:
            self.logger.debug("Awaiting new connection")
            try:
                conn, addr = self.socket.accept_client()
            except OSError:  # SIGINT received
                return
            self.logger.debug("Connection accepted")
            worker = threading.Thread(target=handle_client_connection, args=(conn, addr))
            worker.setDaemon(True)
            worker.start()
            self.logger.debug("Started worker thread")

    def shutdown(self):
        self.logger.debug("Closing socket")
        self.socket.shutdown()
