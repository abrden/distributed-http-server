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
                self.logger.info("KeyboardInterrupt received. Ending my run")
                break
            if data == b'':
                self.logger.info("Bridge closed remotely. Ending my run")
                break
            self.logger.info("Received request from FE %r", data)
            self.logger.info("Sending request through pipe")
            self.request_pipe.send(data)
            self.logger.info("Request sent through pipe")


class ResponseSender:

    def __init__(self, response_pipe, bridge):
        self.logger = logging.getLogger("ResponseSenderThread")

        self.response_pipe = response_pipe
        self.bridge = bridge

    def run(self):
        while True:
            data = self.response_pipe.receive()
            if data is None:
                self.logger.info("Pipe closed remotely. Ending my run")
                raise KeyboardInterrupt
            self.logger.info("Received response from pipe %r", data)
            self.logger.info("Sending response through bridge")
            self.bridge.answer_request(data)


class BackEndServer:

    def __init__(self, front_end_host, front_end_port, cache_size, locks_pool_size, workers_num):
        self.logger = logging.getLogger("BackEndServer")

        self.logger.info("Instantiating pipes")
        request_p_out, request_p_in = Pipe(duplex=False)
        response_p_out, response_p_in = Pipe(duplex=False)

        self.request_pipe = PipeWrite(request_p_in)
        self.response_pipe = PipeRead(response_p_out)

        self.logger.info("Building bridge with FE")
        self.bridge = Bridge(front_end_host, front_end_port)

        self.logger.info("Starting RequestReceiver Thread")
        self.req_receiver_thread = RequestReceiverThread(self.request_pipe, self.bridge)
        self.req_receiver_thread.start()

        self.logger.info("Starting FileManager Process")
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
        self.logger.info("Closing Bridge")
        self.bridge.shutdown()
        self.logger.info("Closing Pipes")
        self.request_pipe.close()
        self.response_pipe.close()
        self.logger.info("Joining RequestReceiver Thread")
        self.req_receiver_thread.join()
        self.logger.info("Joining FileManager Process")
        self.file_manager_process.join()
