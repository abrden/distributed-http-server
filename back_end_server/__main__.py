import os
import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(threadName)s: %(message)s")

from .back_end_server import BackEndServer


def main():
    logger = logging.getLogger("BE-Server")
    logger.info("Starting BE Server")

    s = BackEndServer(os.environ['FE_IP'], int(os.environ['FE_PORT']), int(os.environ['CACHE_SIZE']))
    s.start()

    logger.info("Done")


if __name__ == "__main__":
    main()
