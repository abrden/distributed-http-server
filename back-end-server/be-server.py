import signal
import threading
import logging
logging.basicConfig(level=logging.DEBUG)

from HTTPServer import HTTPServer


def main():
    logger = logging.getLogger("BEServer")

    def graceful_shutdown(sig, dummy):
        s.shutdown()
        main_thread = threading.current_thread()
        for thread in threading.enumerate():
            if thread is main_thread:
                continue
            logger.debug('Joining %s', thread.getName())
            thread.join()

    signal.signal(signal.SIGINT, graceful_shutdown)

    logger.info("Starting BE Server")
    s = HTTPServer('127.0.0.1', 5001)
    s.wait_for_connections()
    logger.info("Done")


if __name__ == "__main__":
    main()
