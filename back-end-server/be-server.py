import multiprocessing

from HTTPServer import HTTPServer

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    server = HTTPServer('', 5000)
    try:
        logging.info("Listening")
        server.start()
    except:
        logging.exception("Unexpected exception")
    finally:
        logging.info("Shutting down")
        for process in multiprocessing.active_children():
            logging.info("Shutting down process %r", process)
            process.terminate()
            process.join()
    logging.info("All done")
