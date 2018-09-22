import sys
import signal
import logging
logging.basicConfig(level=logging.DEBUG)

from .front_end_server import FrontEndServer


def main():
    logger = logging.getLogger("FE-Server")
    logger.info("Starting FE Server")

    s = FrontEndServer(sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
    s.start()

    logger.info("Done")


main()
