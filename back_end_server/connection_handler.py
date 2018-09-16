import logging
logging.basicConfig(level=logging.DEBUG)

from http_server.httpserver import HTTPResponseEncoder, HTTPRequestDecoder
from http_server.sockets import ClientSocket
from .cache.ThreadSafeLRUCache import ThreadSafeLRUCache


def fulfill_request(whoami, cache, verb, path, body=None):
    logger = logging.getLogger(whoami)
    if verb == 'GET':
        if cache.hasEntry(path):
            logger.debug("Cache HIT: %r", path)
            cached_response = cache.getEntry(path)
            return HTTPResponseEncoder.encode(200, cached_response)
        else:
            logger.debug("Cache MISS: %r", path)
            try:
                # TODO search in file system
                response_content = "<html><body><p>Hello world!</p><p>From BE HTTP server</p></body></html>"
                logger.debug("File found: %r", path)

            except IOError:
                logger.debug("File not found: %r", path)
                return HTTPResponseEncoder.encode(404)

            cache.loadEntry(path, response_content)
            return HTTPResponseEncoder.encode(200, response_content)

    elif verb == 'POST':
        return HTTPResponseEncoder.encode(501)

    elif verb == 'PUT':
        return HTTPResponseEncoder.encode(501)

    elif verb == 'DELETE':
        return HTTPResponseEncoder.encode(501)


class ConnectionHandler:

    def __init__(self, cache_size):
        self.cache = ThreadSafeLRUCache(cache_size)

    def handle(self, conn, address):
        whoami = "Worker-%r" % (address,)
        logger = logging.getLogger(whoami)

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

            response = fulfill_request(whoami, self.cache, verb, path)

            conn.send(response)
            logger.debug("Sent data %r", response)

        except:
            logger.exception("Problem handling request")

        finally:
            logger.debug("Closing connection with client")
            conn.close()
