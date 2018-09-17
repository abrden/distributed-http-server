import logging
logging.basicConfig(level=logging.DEBUG)

from http_server.httpserver import HTTPResponseEncoder, HTTPRequestDecoder
from .cache.ThreadSafeLRUCache import ThreadSafeLRUCache
from .file_handler import FileHandler
from .bridge import Bridge


class BackEndServer:

    def __init__(self, front_end_host, front_end_port, cache_size):
        self.logger = logging.getLogger('BackEndServer')
        self.cache = ThreadSafeLRUCache(cache_size)
        self.bridge = Bridge(front_end_host, front_end_port)

    def start(self):
        while True:
            try:
                data = self.bridge.receive_request()
                self.logger.debug("Received data %r", data)

                verb, path, version, headers, body = HTTPRequestDecoder.decode(data)
                self.logger.debug("Verb %r", verb)
                self.logger.debug("Path %r", path)
                self.logger.debug("Version %r", version)
                self.logger.debug("Headers %r", headers)
                self.logger.debug("Body %r", body)

                response = self.fulfill_request(self.cache, verb, path, body)

                self.bridge.answer_request(response)
                self.logger.debug("Sent data %r", response)

            except:
                self.logger.exception("Problem handling request")

    def fulfill_request(self, cache, verb, path, body=None):
        if path == "/":
            self.logger.debug("Empty path: %r", path)
            return HTTPResponseEncoder.encode(400, 'URI should be /{origin}/{entity}/{id}\n')

        if verb == 'GET':
            if cache.hasEntry(path):
                self.logger.debug("Cache HIT: %r", path)
                cached_response = cache.getEntry(path)
                return HTTPResponseEncoder.encode(200, cached_response)
            else:
                self.logger.debug("Cache MISS: %r", path)
                try:
                    response_content = FileHandler.fetch_file(path)
                    self.logger.debug("File found: %r", path)

                except IOError:
                    self.logger.debug("File not found: %r", path)
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

    def shutdown(self):
        self.bridge.shutdown()
