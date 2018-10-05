import logging

from connectivity.sockets import LogReceiverSocket


class AuditLogger:

    def __init__(self, host, port, log_file):
        self.logger = logging.getLogger("AuditLogger")
        self.host = host
        self.port = port
        self.log_file = log_file

    def start(self):
        self.logger.info("Connecting to FE")
        conn = LogReceiverSocket(self.host, self.port)

        self.logger.info("Starting log")
        with open(self.log_file, "a+") as f:
            f.write("LOG START\r\n")
            while True:
                self.logger.info("Receiving new log")
                new_log = conn.receive()
                if new_log is None:
                    self.logger.debug("EOF received at the end of log socket")
                    break
                self.logger.info("Decoding new log")
                date, addr, method, status = new_log
                self.logger.info("Writing new log")
                f.write("{date} {addr} {request_method} {status}\r\n".format(date=date,
                                                                             addr=addr,
                                                                             request_method=method,
                                                                             status=status))
            conn.close()
