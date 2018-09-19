import sys
import signal
import logging
logging.basicConfig(level=logging.DEBUG)

from http_server.httpserver import HTTPServer
from .connection_handler import RequestReceiverThread


def main():
    logger = logging.getLogger("FE-Server")

    def graceful_shutdown(sig, dummy):
        s.shutdown()
        handler.close_bridge()

    signal.signal(signal.SIGINT, graceful_shutdown)

    logger.info("Starting FE Server")
    handler = RequestReceiverThread(sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
    s = HTTPServer(sys.argv[1], int(sys.argv[2]), handler)
    s.wait_for_connections()
    logger.info("Done")


main()
