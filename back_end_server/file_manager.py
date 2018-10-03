import logging
from multiprocessing import Process
from multiprocessing.dummy import Pool

from connectivity.http import HTTPRequestDecoder
from .cache.ThreadSafeLRUCache import ThreadSafeLRUCache
from concurrency.pipes import PipeRead, PipeWrite
from .request_handler import RequestHandler


class FileManagerWorker:

    @staticmethod
    def work(response_pipe, cache, req):
        logger = logging.getLogger("FileManagerWorker")
        logger.debug("Working on request %r", req)

        request_handler = RequestHandler(cache)

        verb, path, version, headers, body = HTTPRequestDecoder.decode(req)
        res = request_handler.handle(headers['Request-Id'], verb, path, body)

        logger.info("Sending response through pipe %r", res)
        response_pipe.send(res)


class FileManager(Process):

    def __init__(self, cache_size, requests_p_out, response_p_in, workers_num):
        super(FileManager, self).__init__()

        self.logger = logging.getLogger("FileManager")

        self.logger.info("Initializing cache with size %r", cache_size)
        self.cache = ThreadSafeLRUCache(cache_size)

        self.request_pipe = PipeRead(requests_p_out)
        self.response_pipe = PipeWrite(response_p_in)

        self.workers = workers_num

        self.start()

    def run(self):
        pool = Pool(self.workers)

        while True:
            self.logger.info("Waiting for request at the end of requests pipe")
            req = self.request_pipe.receive()
            if req is None:
                self.logger.info("Pipe closed. Ending my run")
                break

            self.logger.info("Adding request to workers pool")
            pool.apply_async(FileManagerWorker.work, (self.response_pipe, self.cache, req))

        self.logger.debug("Closing workers pool")
        pool.close()
        self.logger.debug("Joining workers pool")
        pool.join()
        self.shutdown()

    def shutdown(self):
        self.logger.info("Closing pipes")
        self.request_pipe.close()
        self.response_pipe.close()
