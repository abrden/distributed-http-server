from multiprocessing import Process, Pipe
from threading import Thread
import logging

logging.basicConfig(level=logging.DEBUG)

from connectivity.http import HTTPResponseEncoder, HTTPRequestDecoder
from .cache.ThreadSafeLRUCache import ThreadSafeLRUCache
from .file_handler import FileHandler
from .bridge import Bridge
from concurrency.pipes import PipeRead, PipeWrite


class FileManagerWorker(Thread):

    def __init__(self, response_pipe, cache, req):
        super(FileManagerWorker, self).__init__()

        self.logger = logging.getLogger('FileManagerWorker-%r' % self.getName())

        self.cache = cache
        self.response_pipe = response_pipe
        self.req = req

        self.start()

    def run(self):
        self.logger.debug("Working on request %r", self.req)

        verb, path, version, headers, body = HTTPRequestDecoder.decode(self.req)
        self.logger.debug("Verb %r", verb)
        self.logger.debug("Path %r", path)
        self.logger.debug("Version %r", version)
        self.logger.debug("Headers %r", headers)
        self.logger.debug("Body %r", body)

        res = self.fulfill_request(headers['Request-Id'], verb, path, body)
        self.logger.debug("Sending response through pipe %r", res)
        self.response_pipe.send(res)

    def fulfill_request(self, req_id, verb, path, body=None):
        if path == "/":
            self.logger.debug("Empty path: %r", path)
            return HTTPResponseEncoder.encode(400, verb, req_id, 'URI should be /{origin}/{entity}/{id}\n')

        if verb == 'GET':
            if self.cache.has_entry(path):
                self.logger.debug("Cache HIT: %r", path)
                cached_response = self.cache.get_entry(path)
                return HTTPResponseEncoder.encode(200, verb, req_id, cached_response)
            else:
                self.logger.debug("Cache MISS: %r", path)
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


class FileManager(Process):

    def __init__(self, cache_size, requests_p_out, response_p_in):
        super(FileManager, self).__init__()

        self.logger = logging.getLogger('FileManager')

        self.logger.debug("Initializing cache with size %r", cache_size)
        self.cache = ThreadSafeLRUCache(cache_size)

        self.request_pipe = PipeRead(requests_p_out)
        self.response_pipe = PipeWrite(response_p_in)

        self.workers = []

        self.start()

    def run(self):
        while True:
            self.logger.debug("Waiting for request at the end of req pipe")
            req = self.request_pipe.receive()
            if req is None:
                self.logger.debug("Pipe closed. Ending my run")
                break
            self.logger.debug("Creating a worker to take the request")
            worker = FileManagerWorker(self.response_pipe, self.cache, req)
            self.workers.append(worker)

        self.shutdown()

    def shutdown(self):
        self.logger.debug("Closing pipes")
        self.request_pipe.close()
        self.response_pipe.close()
        self.logger.debug("Joining my workers")
        for w in self.workers:
            w.join()


class RequestReceiverThread(Thread):  # Name in terms of the client

    def __init__(self, request_pipe, bridge):
        Thread.__init__(self)
        self.logger = logging.getLogger('RequestReceiverThread')

        self.request_pipe = request_pipe

        self.bridge = bridge

        self.start()

    def run(self):
        while True:
            try:
                data = self.bridge.receive_request()
            except (KeyboardInterrupt, OSError):
                self.logger.debug("KeyboardInterrupt received. Ending my run")
                break
            if data == b'':
                self.logger.debug("Bridge closed remotely. Ending my run")
                break
            self.logger.debug("Received request from bridge %r", data)
            self.logger.debug("Sending request through pipe")
            self.request_pipe.send(data)
            self.logger.debug("Request sent through pipe")


class ResponseSenderThread(Thread):

    def __init__(self, response_pipe, bridge):
        Thread.__init__(self)
        self.logger = logging.getLogger("ResponseSenderThread")

        self.response_pipe = response_pipe

        self.bridge = bridge

        # self.start()

    def run(self):
        while True:
            data = self.response_pipe.receive()
            if data is None:
                self.logger.debug("Pipe closed remotely. Ending my run")
                break
            self.logger.debug("Received response from pipe %r", data)
            self.logger.debug("Sending response through bridge")
            self.bridge.answer_request(data)


class BackEndServer:

    def __init__(self, front_end_host, front_end_port, cache_size):
        self.logger = logging.getLogger("BackEndServer")

        self.logger.debug("Instantiating pipes")
        request_p_out, request_p_in = Pipe(duplex=False)
        response_p_out, response_p_in = Pipe(duplex=False)

        self.request_pipe = PipeWrite(request_p_in)
        self.response_pipe = PipeRead(response_p_out)

        self.logger.debug("Building bridge with FE")
        self.bridge = Bridge(front_end_host, front_end_port)

        self.logger.debug("Starting RequestReceiver Thread")
        self.req_receiver_thread = RequestReceiverThread(self.request_pipe, self.bridge)

        self.logger.debug("Starting FileManager Process")
        self.file_manager_process = FileManager(cache_size, request_p_out, response_p_in)

        self.logger.debug("Closing unused pipe fds")
        request_p_out.close()
        response_p_in.close()

        # self.res_sender_thread = ResponseSenderThread(self.response_pipe, self.bridge)

    def start(self):
        res_sender_thread = ResponseSenderThread(self.response_pipe, self.bridge)
        res_sender_thread.run()
        self.shutdown()

    def shutdown(self):
        self.logger.debug("Closing Bridge")
        self.bridge.shutdown()
        self.logger.debug("Closing Pipes")
        self.request_pipe.close()
        self.response_pipe.close()
        self.logger.debug("Joining RequestReceiver Thread")
        self.req_receiver_thread.join()
        # self.res_sender_thread.join()
        self.logger.debug("Joining FileManager Process")
        self.file_manager_process.join()
