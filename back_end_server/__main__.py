import sys
import signal
import logging
logging.basicConfig(level=logging.DEBUG)

from .back_end_server import BackEndServer


def main():
    logger = logging.getLogger("BE-Server")

    #def graceful_shutdown(sig, dummy):
    #    s.shutdown()

    #signal.signal(signal.SIGINT, graceful_shutdown)

    try:
        logger.info("Starting BE Server")
        s = BackEndServer(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
        s.start()

    except:
        s.shutdown()

    finally:
        logger.info("Done")


main()
