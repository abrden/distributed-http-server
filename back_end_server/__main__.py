import sys
import signal
import logging
logging.basicConfig(level=logging.DEBUG)

from .back_end_server import BackEndServer


def main():
    logger = logging.getLogger("BE-Server")
    logger.info("Starting BE Server")

    s = BackEndServer(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    s.start()

    logger.info("Done")


main()
