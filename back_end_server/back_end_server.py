from multiprocessing import Pipe
from threading import Thread
import logging

from .bridge import Bridge
from concurrency.pipes import PipeRead, PipeWrite
from .file_manager import FileManager


class RequestReceiverThread(Thread):

    def __init__(self, request_pipe, bridge):
        super(RequestReceiverThread, self).__init__()
        self.logger = logging.getLogger('RequestReceiverThread')

        self.request_pipe = request_pipe
        self.bridge = bridge

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


class ResponseSender:

    def __init__(self, response_pipe, bridge):
        self.logger = logging.getLogger("ResponseSenderThread")

        self.response_pipe = response_pipe
        self.bridge = bridge

    def run(self):
        while True:
            data = self.response_pipe.receive()
            if data is None:
                self.logger.debug("Pipe closed remotely. Ending my run")
                raise KeyboardInterrupt
            self.logger.debug("Received response from pipe %r", data)
            self.logger.debug("Sending response through bridge")
            self.bridge.answer_request(data)


class BackEndServer:

    def __init__(self, front_end_host, front_end_port, cache_size, locks_pool_size, workers_num):
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
        self.req_receiver_thread.start()

        self.logger.debug("Starting FileManager Process")
        self.file_manager_process = FileManager(cache_size, locks_pool_size, request_p_out, response_p_in, workers_num)

        self.logger.debug("Closing unused pipe fds")
        request_p_out.close()
        response_p_in.close()

    def start(self):
        res_sender_thread = ResponseSender(self.response_pipe, self.bridge)
        try:
            res_sender_thread.run()
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        self.logger.debug("Closing Bridge")
        self.bridge.shutdown()
        self.logger.debug("Closing Pipes")
        self.request_pipe.close()
        self.response_pipe.close()
        self.logger.debug("Joining RequestReceiver Thread")
        self.req_receiver_thread.join()
        self.logger.debug("Joining FileManager Process")
        self.file_manager_process.join()
