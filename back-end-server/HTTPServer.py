import threading
import time
import logging

logging.basicConfig(level=logging.DEBUG)

from sockets import Socket


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
        h += 'Connection: close\r\n\r\n'

        return h


class HTTPServer:

    def __init__(self, host, port, conn_handler):
        self.logger = logging.getLogger("BEHTTPServer")
        self.socket = Socket(host, port)
        self.conn_handler = conn_handler

    def wait_for_connections(self):
        while True:
            self.logger.debug("Awaiting new connection")
            try:
                conn, addr = self.socket.accept_client()
            except OSError:  # SIGINT received
                return
            self.logger.debug("Connection accepted")
            worker = threading.Thread(target=self.conn_handler, args=(conn, addr))
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
            logger.debug('Joining %s', thread.getName())
            thread.join()
