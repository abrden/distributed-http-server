import logging
logging.basicConfig(level=logging.DEBUG)

from http_server.httpserver import HTTPResponseMaker
from http_server.sockets import ClientSocket


def handle_client_connection(conn, address):
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("Worker-%r" % (address,))

    try:
        conn = ClientSocket(conn)

        logger.debug("Connected %r at %r", conn, address)

        data = conn.receive(1024)  # receive data from client
        logger.debug("Received data %r", data)

        string = bytes.decode(data)

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
