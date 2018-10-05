import os
import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(threadName)s: %(message)s")

from .front_end_server import FrontEndServer


def main():
    logger = logging.getLogger("FE-Server")
    logger.info("Starting FE Server")

    s = FrontEndServer(os.environ['HOST'],
                       int(os.environ['HTTP_SERVER_PORT']),
                       os.environ['HOST'],
                       int(os.environ['BRIDGE_PORT']),
                       os.environ['HOST'],
                       int(os.environ['LOGGER_PORT']),
                       int(os.environ['BE_NUM']),
                       int(os.environ['RECEIVERS_NUM']))
    s.start()

    logger.info("Done")


if __name__ == "__main__":
    main()
