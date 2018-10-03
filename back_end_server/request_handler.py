import logging

from .file_handler import FileHandler
from connectivity.http import HTTPResponseEncoder

GET_VERB = 'GET'
POST_VERB = 'POST'
PUT_VERB = 'PUT'
DELETE_VERB = 'DELETE'


class RequestHandler:

    def __init__(self, cache, locks_pool_size):
        self.logger = logging.getLogger('RequestHandler')
        self.cache = cache
        self.file_handler = FileHandler(locks_pool_size)

    def handle(self, req_id, verb, path, body=None):
        if path == "/":
            self.logger.debug("Empty path: %r", path)
            return HTTPResponseEncoder.encode(400, verb, req_id, 'URI should be /{origin}/{entity}/{id}\n')

        if verb == GET_VERB:
            return self._handle_get(req_id, path)
        elif verb == POST_VERB:
            return self._handle_post(req_id, path, body)
        elif verb == PUT_VERB:
            return self._handle_put(req_id, path, body)
        elif verb == DELETE_VERB:
            return self._handle_delete(req_id, path)
        else:
            return self._handle_unknown(req_id, verb)

    def _handle_get(self, req_id, path):
        if self.cache.has_entry(path):
            self.logger.info("Cache HIT: %r", path)
            cached_response = self.cache.get_entry(path)
            return HTTPResponseEncoder.encode(200, GET_VERB, req_id, cached_response)
        else:
            self.logger.info("Cache MISS: %r", path)
            try:
                response_content = self.file_handler.fetch_file(path)
                self.logger.debug("File found: %r", path)

            except IOError:
                self.logger.debug("File not found: %r", path)
                return HTTPResponseEncoder.encode(404, GET_VERB, req_id, 'File not found\n')

            self.cache.load_entry(path, response_content)
            return HTTPResponseEncoder.encode(200, GET_VERB, req_id, response_content)

    def _handle_post(self, req_id, path, body):
        try:
            self.file_handler.create_file(path, body)

        except RuntimeError:
            self.logger.debug("File already exists: %r", path)
            return HTTPResponseEncoder.encode(409, POST_VERB, req_id, 'A file with that URI already exists\n')

        self.cache.load_entry(path, body)
        return HTTPResponseEncoder.encode(201, POST_VERB, req_id, 'Created\n')

    def _handle_put(self, req_id, path, body):
        try:
            self.file_handler.update_file(path, body)

        except IOError:
            self.logger.debug("File not found: %r", path)
            return HTTPResponseEncoder.encode(404, PUT_VERB, req_id, 'File not found\n')

        self.cache.load_entry(path, body)
        return HTTPResponseEncoder.encode(204, PUT_VERB, req_id)

    def _handle_delete(self, req_id, path):
        try:
            self.file_handler.delete_file(path)

        except IOError:
            self.logger.debug("File not found: %r", path)
            return HTTPResponseEncoder.encode(404, DELETE_VERB, req_id, 'File not found\n')

        self.cache.delete_entry(path)
        return HTTPResponseEncoder.encode(204, DELETE_VERB, req_id)

    def _handle_unknown(self, req_id, verb):
        self.logger.debug("Unknown request method: %r", verb)
        return HTTPResponseEncoder.encode(501, verb, req_id, 'Unknown request method\n')
