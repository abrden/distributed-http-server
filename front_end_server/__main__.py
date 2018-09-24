import os
import logging
logging.basicConfig(level=logging.DEBUG)

from .front_end_server import FrontEndServer


def main():
    logger = logging.getLogger("FE-Server")
    logger.info("Starting FE Server")

    s = FrontEndServer(os.environ['HOST'], int(os.environ['HTTP_SERVER_PORT']), os.environ['FE_HOST'], int(os.environ['BRIDGE_PORT']), int(os.environ['BE_NUM']))
    s.start()

    logger.info("Done")


main()
