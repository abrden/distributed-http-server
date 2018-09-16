import logging
logging.basicConfig(level=logging.DEBUG)

from http_server.httpserver import HTTPResponseEncoder, HTTPRequestDecoder
from http_server.sockets import ClientSocket
from .cache.ThreadSafeLRUCache import ThreadSafeLRUCache
from .file_handler import FileHandler


def fulfill_request(whoami, cache, verb, path, body=None):
    logger = logging.getLogger(whoami)

    if path == "/":
        logger.debug("Empty path: %r", path)
        return HTTPResponseEncoder.encode(400, 'URI should be /{origin}/{entity}/{id}\n')

    if verb == 'GET':
        if cache.hasEntry(path):
            logger.debug("Cache HIT: %r", path)
            cached_response = cache.getEntry(path)
            return HTTPResponseEncoder.encode(200, cached_response)
        else:
            logger.debug("Cache MISS: %r", path)
            try:
                response_content = FileHandler.fetch_file(path)
                logger.debug("File found: %r", path)

            except IOError:
                logger.debug("File not found: %r", path)
                return HTTPResponseEncoder.encode(404, 'File not found\n')

            cache.loadEntry(path, response_content)
            return HTTPResponseEncoder.encode(200, response_content)

    elif verb == 'POST':
        try:
            FileHandler.create_file(path, body)

        except RuntimeError:
            return HTTPResponseEncoder.encode(409, 'A file with that URI already exists\n')

        cache.loadEntry(path, body)
        return HTTPResponseEncoder.encode(201, 'Created\n')

    elif verb == 'PUT':
        return HTTPResponseEncoder.encode(501, 'Not implemented\n')

    elif verb == 'DELETE':
        return HTTPResponseEncoder.encode(501, 'Not implemented\n')


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

            verb, path, version, headers, body = HTTPRequestDecoder.decode(data)
            logger.debug("Verb %r", verb)
            logger.debug("Path %r", path)
            logger.debug("Version %r", version)
            logger.debug("Headers %r", headers)
            logger.debug("Body %r", body)

            response = fulfill_request(whoami, self.cache, verb, path, body)

            conn.send(response)
            logger.debug("Sent data %r", response)

        except:
            logger.exception("Problem handling request")

        finally:
            logger.debug("Closing connection with client")
            conn.close()
