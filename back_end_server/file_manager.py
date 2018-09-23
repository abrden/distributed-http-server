import logging
from multiprocessing import Process
from threading import Thread

from connectivity.http import HTTPResponseEncoder, HTTPRequestDecoder
from .file_handler import FileHandler
from .cache.ThreadSafeLRUCache import ThreadSafeLRUCache
from concurrency.pipes import PipeRead, PipeWrite


class FileManager(Process):

    def __init__(self, cache_size, requests_p_out, response_p_in):
        super(FileManager, self).__init__()

        self.logger = logging.getLogger('FileManager')

        self.logger.info("Initializing cache with size %r", cache_size)
        self.cache = ThreadSafeLRUCache(cache_size)

        self.request_pipe = PipeRead(requests_p_out)
        self.response_pipe = PipeWrite(response_p_in)

        self.workers = []

        self.start()

    def run(self):
        while True:
            self.logger.info("Waiting for request at the end of requests pipe")
            req = self.request_pipe.receive()
            if req is None:
                self.logger.info("Pipe closed. Ending my run")
                break
            self.logger.info("Creating a worker to take the request")
            worker = FileManagerWorker(self.response_pipe, self.cache, req)
            self.workers.append(worker)

        self.shutdown()

    def shutdown(self):
        self.logger.info("Closing pipes")
        self.request_pipe.close()
        self.response_pipe.close()
        self.logger.info("Joining my workers")
        for w in self.workers:
            w.join()


class FileManagerWorker(Thread):

    def __init__(self, response_pipe, cache, req):
        super(FileManagerWorker, self).__init__()

        self.logger = logging.getLogger('FileManagerWorker-%r' % self.getName())

        self.cache = cache
        self.response_pipe = response_pipe
        self.req = req

        self.start()

    def run(self):
        self.logger.info("Working on request %r", self.req)

        verb, path, version, headers, body = HTTPRequestDecoder.decode(self.req)
        self.logger.debug("Verb %r", verb)
        self.logger.debug("Path %r", path)
        self.logger.debug("Version %r", version)
        self.logger.debug("Headers %r", headers)
        self.logger.debug("Body %r", body)

        res = self.fulfill_request(headers['Request-Id'], verb, path, body)
        self.logger.info("Sending response through pipe %r", res)
        self.response_pipe.send(res)

    def fulfill_request(self, req_id, verb, path, body=None):
        if path == "/":
            self.logger.debug("Empty path: %r", path)
            return HTTPResponseEncoder.encode(400, verb, req_id, 'URI should be /{origin}/{entity}/{id}\n')

        if verb == 'GET':
            if self.cache.has_entry(path):
                self.logger.info("Cache HIT: %r", path)
                cached_response = self.cache.get_entry(path)
                return HTTPResponseEncoder.encode(200, verb, req_id, cached_response)
            else:
                self.logger.info("Cache MISS: %r", path)
                try:
                    response_content = FileHandler.fetch_file(path)
                    self.logger.debug("File found: %r", path)

                except IOError:
                    self.logger.debug("File not found: %r", path)
                    return HTTPResponseEncoder.encode(404, verb, req_id, 'File not found\n')

                self.cache.load_entry(path, response_content)
                return HTTPResponseEncoder.encode(200, verb, req_id, response_content)

        elif verb == 'POST':
            try:
                FileHandler.create_file(path, body)

            except RuntimeError:
                return HTTPResponseEncoder.encode(409, verb, req_id, 'A file with that URI already exists\n')

            self.cache.load_entry(path, body)
            return HTTPResponseEncoder.encode(201, verb, req_id, 'Created\n')

        elif verb == 'PUT':
            try:
                FileHandler.update_file(path, body)

            except IOError:
                return HTTPResponseEncoder.encode(404, verb, req_id, 'File not found\n')

            self.cache.load_entry(path, body)
            return HTTPResponseEncoder.encode(204, verb, req_id)

        elif verb == 'DELETE':
            try:
                FileHandler.delete_file(path)

            except IOError:
                return HTTPResponseEncoder.encode(404, verb, req_id, 'File not found\n')

            self.cache.delete_entry(path)
            return HTTPResponseEncoder.encode(204, verb, req_id)
