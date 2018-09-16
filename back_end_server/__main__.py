import sys
import signal
import logging
logging.basicConfig(level=logging.DEBUG)

from http_server.httpserver import HTTPServer
from .connection_handler import ConnectionHandler


def main():
    logger = logging.getLogger("BEServer")

    def graceful_shutdown(sig, dummy):
        s.shutdown()

    signal.signal(signal.SIGINT, graceful_shutdown)

    logger.info("Starting BE Server")
    handler = ConnectionHandler(int(sys.argv[3]))
    s = HTTPServer(sys.argv[1], int(sys.argv[2]), handler)
    s.wait_for_connections()
    logger.info("Done")


main()
