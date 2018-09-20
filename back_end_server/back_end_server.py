from multiprocessing import Process, Pipe
from threading import Thread
import logging

logging.basicConfig(level=logging.DEBUG)

from http_server.httpserver import HTTPResponseEncoder, HTTPRequestDecoder
from .cache.ThreadSafeLRUCache import ThreadSafeLRUCache
from .file_handler import FileHandler
from .bridge import Bridge
from .concurrency.pipes import PipeRead, PipeWrite


class FileManager(Process):

    def __init__(self, cache_size, requests_p_in, requests_p_out, response_p_in, response_p_out):
        super(FileManager, self).__init__()

        self.logger = logging.getLogger('FileManager')

        self.logger.debug("Initializing cache with size %r", cache_size)
        self.cache = ThreadSafeLRUCache(cache_size)

        requests_p_in.close()
        response_p_out.close()

        self.request_pipe = PipeRead(requests_p_out)
        self.response_pipe = PipeWrite(response_p_in)

        self.workers = []

        self.daemon = True
        self.start()

    def run(self):
        self.logger.debug("Creating worker threads")
        for _ in range(1):  # TODO Make customizable
            worker = Thread(target=self.work)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
            for w in self.workers:
                w.join()

    def shutdown(self):
        self.request_pipe.close()
        self.response_pipe.close()

    def work(self):
        while True:
            self.logger.debug("Waiting for request at the end of req pipe")
            req = self.request_pipe.receive()
            self.logger.debug("Request received from pipe %r", req)

            verb, path, version, headers, body = HTTPRequestDecoder.decode(req)
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
            return (req_id + '\r\n').encode() + HTTPResponseEncoder.encode(400, 'URI should be /{origin}/{entity}/{id}\n')

        if verb == 'GET':
            if self.cache.hasEntry(path):
                self.logger.debug("Cache HIT: %r", path)
                cached_response = self.cache.getEntry(path)
                return (req_id + '\r\n').encode() + HTTPResponseEncoder.encode(200, cached_response)
            else:
                self.logger.debug("Cache MISS: %r", path)
                try:
                    response_content = FileHandler.fetch_file(path)
                    self.logger.debug("File found: %r", path)

                except IOError:
                    self.logger.debug("File not found: %r", path)
                    return (req_id + '\r\n').encode() + HTTPResponseEncoder.encode(404, 'File not found\n')

                self.cache.loadEntry(path, response_content)
                return (req_id + '\r\n').encode() + HTTPResponseEncoder.encode(200, response_content)

        elif verb == 'POST':
            try:
                FileHandler.create_file(path, body)

            except RuntimeError:
                return (req_id + '\r\n').encode() + HTTPResponseEncoder.encode(409, 'A file with that URI already exists\n')

            self.cache.loadEntry(path, body)
            return (req_id + '\r\n').encode() + HTTPResponseEncoder.encode(201, 'Created\n')

        elif verb == 'PUT':
            return (req_id + '\r\n').encode() + HTTPResponseEncoder.encode(501, 'Not implemented\n')

        elif verb == 'DELETE':
            return (req_id + '\r\n').encode() + HTTPResponseEncoder.encode(501, 'Not implemented\n')


class RequestReceiverThread(Thread):

    def __init__(self, request_pipe, bridge):
        Thread.__init__(self)
        self.logger = logging.getLogger('RequestReceiverThread')

        self.request_pipe = request_pipe

        self.bridge = bridge

        self.daemon = True
        self.start()

    def run(self):
        while True:
            data = self.bridge.receive_request()
            if data == b'':
                self.logger.debug("Bridge closed remotely")
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

        #self.daemon = True
        #self.start()

    def run(self):
        while True:
            data = self.response_pipe.receive()
            if data == b'':  # TODO FIX
                self.logger.debug("Pipe closed remotely")
                break
            self.logger.debug("Received response from pipe %r", data)
            self.logger.debug("Sending response through bridge")
            self.bridge.answer_request(data)


class BackEndServer:

    def __init__(self, front_end_host, front_end_port, cache_size):
        self.logger = logging.getLogger("BackEndServer")

        self.logger.debug("Instantiating pipes")
        request_p_out, request_p_in = Pipe()
        response_p_out, response_p_in = Pipe()

        self.logger.debug("Starting FileManagerProcess")
        self.file_manager_process = FileManager(cache_size, request_p_in, request_p_out, response_p_in, response_p_out)

        self.logger.debug("Building bridge with FE")
        self.bridge = Bridge(front_end_host, front_end_port)

        request_p_out.close()
        response_p_in.close()

        self.request_pipe = PipeWrite(request_p_in)
        self.response_pipe = PipeRead(response_p_out)
        #self.req_receiver_thread = RequestReceiverThread(self.requests_p_in, self.bridge)

        self.res_sender_thread = ResponseSenderThread(self.response_pipe, self.bridge)

    def start(self):
        receiver = RequestReceiverThread(self.request_pipe, self.bridge)
        receiver.run()

    def shutdown(self):
        self.bridge.shutdown()
        #self.req_receiver_thread.join()
        self.res_sender_thread.join()
        self.file_manager_process.join()
        self.request_pipe.close()
        self.response_pipe.close()
