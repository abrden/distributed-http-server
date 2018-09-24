import logging
from multiprocessing import Process
from threading import Thread

from connectivity.http import HTTPRequestDecoder
from .cache.ThreadSafeLRUCache import ThreadSafeLRUCache
from concurrency.pipes import PipeRead, PipeWrite
from .request_handler import RequestHandler


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

        self.request_handler = RequestHandler(cache, self.getName())

        self.start()

    def run(self):
        self.logger.info("Working on request %r", self.req)

        verb, path, version, headers, body = HTTPRequestDecoder.decode(self.req)

        res = self.request_handler.handle(headers['Request-Id'], verb, path, body)
        self.logger.info("Sending response through pipe %r", res)
        self.response_pipe.send(res)
