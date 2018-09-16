import sys, os
import signal
import logging
logging.basicConfig(level=logging.DEBUG)

sys.path.append(os.path.abspath(os.path.join('..', 'http-server')))
from httpserver import HTTPServer
from connection_handler import handle_client_connection


def main():
    logger = logging.getLogger("BEServer")

    def graceful_shutdown(sig, dummy):
        s.shutdown()

    signal.signal(signal.SIGINT, graceful_shutdown)

    logger.info("Starting BE Server")
    s = HTTPServer(sys.argv[1], int(sys.argv[2]), handle_client_connection)
    s.wait_for_connections()
    logger.info("Done")


if __name__ == "__main__":
    main()
