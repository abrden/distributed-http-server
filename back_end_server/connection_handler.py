import logging
logging.basicConfig(level=logging.DEBUG)

from http_server.httpserver import HTTPResponseMaker, HTTPRequestDecoder
from http_server.sockets import ClientSocket
from .cache.ThreadSafeLRUCache import ThreadSafeLRUCache


def fulfill_request(cache, verb, path, body=None):
    if verb == 'GET':
        if cache.hasEntry(path):
            cached_response = cache.getEntry(path)
            return HTTPResponseMaker.response(200) + cached_response.encode()
        else:
            try:
                # TODO search in file system
                response_content = "<html><body><p>Hello world!</p><p>From BE HTTP server</p></body></html>"

            except IOError:
                return HTTPResponseMaker.response(404)

            cache.loadEntry(path, response_content)
            return HTTPResponseMaker.response(200) + response_content.encode()

    elif verb == 'POST':
        return HTTPResponseMaker.response(501)

    elif verb == 'PUT':
        return HTTPResponseMaker.response(501)

    elif verb == 'DELETE':
        return HTTPResponseMaker.response(501)


class ConnectionHandler:

    def __init__(self, cache_size):
        self.cache = ThreadSafeLRUCache(cache_size)

    def handle(self, conn, address):
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

            response = fulfill_request(self.cache, verb, path)

            conn.send(response)
            logger.debug("Sent data %r", response)

        except:
            logger.exception("Problem handling request")

        finally:
            logger.debug("Closing connection with client")
            conn.close()
