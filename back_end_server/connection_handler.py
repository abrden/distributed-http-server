import logging
logging.basicConfig(level=logging.DEBUG)

from http_server.httpserver import HTTPResponseMaker, HTTPRequestDecoder
from http_server.sockets import ClientSocket


def fullfill_request(verb, path, body=None):
    if verb == 'GET':
        response_headers = HTTPResponseMaker.response(404)
        response_content = b"<html><body><p>Error 404: File not found</p><p>Python HTTP server</p></body></html>"

        server_response = response_headers
        server_response += response_content

        return server_response
    elif verb == 'POST':
        return HTTPResponseMaker.response(501)

    elif verb == 'PUT':
        return HTTPResponseMaker.response(501)

    elif verb == 'DELETE':
        return HTTPResponseMaker.response(501)


def handle_client_connection(conn, address):
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("Worker-%r" % (address,))

    try:
        conn = ClientSocket(conn)
        logger.debug("Connected %r at %r", conn, address)

        data = conn.receive(1024)  # TODO receive up to request ending
        logger.debug("Received data %r", data)

        verb, path, version, headers = HTTPRequestDecoder.decode(data)
        logger.debug("Verb %r", verb)
        logger.debug("Path %r", path)
        logger.debug("Version %r", version)
        logger.debug("Headers %r", headers)

        response = fullfill_request(verb, path)

        conn.send(response)
        logger.debug("Sent data %r", response)

    except:
        logger.exception("Problem handling request")

    finally:
        logger.debug("Closing connection with client")
        conn.close()
