import os
from multiprocessing import Process
import logging

from connectivity.http import HTTPResponseDecoder


class AuditLogger(Process):

    def __init__(self, pipe_out):
        super(AuditLogger, self).__init__()
        self.logger = logging.getLogger("AuditLogger")
        self.pipe_out = pipe_out
        self.file = open(os.environ['LOG_FILE'], "a+")

        self.start()

    def run(self):
        self.file.write("LOG START\r\n")
        while True:
            new_log = self.pipe_out.receive()
            if new_log is None:
                self.logger.debug("EOF received at the end of log pipe")
                break
            [addr, data] = new_log
            self.logger.info("Writing new log")
            status, date, request_method = HTTPResponseDecoder.decode(data)
            self.file.write(
                "{date} {addr}:{port} {request_method} {status}\r\n".format(date=date,
                                                                            addr=addr[0], port=addr[1],
                                                                            request_method=request_method,
                                                                            status=status))
        self.file.close()
        self.pipe_out.close()
