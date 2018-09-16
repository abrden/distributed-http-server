import sys
import signal
import logging
logging.basicConfig(level=logging.DEBUG)

from http_server.httpserver import HTTPServer
from .connection_handler import handle_client_connection


def main():
    logger = logging.getLogger("BEServer")

    def graceful_shutdown(sig, dummy):
        s.shutdown()

    signal.signal(signal.SIGINT, graceful_shutdown)

    logger.info("Starting BE Server")
    s = HTTPServer(sys.argv[1], int(sys.argv[2]), handle_client_connection)
    s.wait_for_connections()
    logger.info("Done")


main()
