import multiprocessing
import time

from sockets import Socket, ClientSocket


def handle_conn(conn, address):
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("Process-%r" % (address,))
    try:
        logger.debug("Connected %r at %r", conn, address)
        client_socket = ClientSocket(conn)
        while True:
            data = client_socket.receive(1024)
            if data == "":
                logger.debug("Socket closed remotely")
                break
            logger.debug("Received data %r", data)
            #
            string = bytes.decode(data)
            request_method = string.split(' ')[0]
            print("Method: ", request_method)
            print("Request body: ", string)
            response = HTTPResponseMaker.response(200)
            print("Response body: ", response)
            #
            client_socket.send(response.encode())
            logger.debug("Sent data %r", response.encode())
    except:
        logger.exception("Problem handling request")
    finally:
        logger.debug("Closing client socket")
        client_socket.close()


class HTTPResponseMaker:

    @staticmethod
    def response(code):
        h = ''
        if code == 200:
            h = 'HTTP/1.1 200 OK\n'
        elif code == 404:
            h = 'HTTP/1.1 404 Not Found\n'
        elif code == 501:
            h = 'HTTP/1.1 501 Not Implemented\n'

        # write further headers
        current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

        h += 'Date: ' + current_date + '\n'
        h += 'Server: BE-HTTP-Server\n'
        h += 'Connection: close\n\n'  # signal that the connection wil be closed after completing the request

        return h


class HTTPServer:

    def __init__(self, host, port):
        import logging
        self.logger = logging.getLogger("HTTPServer")
        self.host = host
        self.port = port
        self.socket = None

    def start(self):
        self.logger.debug("Listening")
        self.socket = Socket(self.host, self.port)

        while True:
            conn, address = self.socket.accept_client()
            self.logger.debug("Connection accepted")
            process = multiprocessing.Process(target=handle_conn, args=(conn, address))
            process.daemon = True
            process.start()
            self.logger.debug("Started process %r", process)

    def end(self):
        self.logger.debug("Closing socket")
        self.socket.close()
