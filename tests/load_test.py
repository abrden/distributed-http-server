from multiprocessing import Process, Pool
import sys
import os
import random
import logging

from request import get, post, put, delete

logging.basicConfig(level=logging.DEBUG)


def generate_random_uri():
    origins = ['netflix', 'spotify', 'almundo', 'pandora', 'hulu']
    resources = ['movies', 'series', 'songs', 'albums', 'artists', 'users']
    return '/' + random.choice(origins) + '/' + random.choice(resources) + '/' + str(random.randint(1, 10))


def random_method():
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    method = random.choice(methods)
    if method == 'GET':
        return method, get
    elif method == 'POST':
        return method, post
    elif method == 'PUT':
        return method, put
    elif method == 'DELETE':
        return method, delete


def generate_random_content():
    jsons = ["{'hello':'world'}", "{'hola':'mundo'}", "{'bonjour':'le monde'}", "{'ciao':'mondo'}"]
    return random.choice(jsons)


def make_requests(host, port, reqs):
    logger = logging.getLogger("Worker-%r" % os.getpid())

    for i in range(reqs):
        uri = generate_random_uri()
        method, f = random_method()
        if method == 'POST' or method == 'PUT':
            content = generate_random_content()
            logger.debug("Making %r request with URI %r and content %r", method, uri, content)
            res = f('http://' + host + ':' + str(port) + uri, content)
        else:
            logger.debug("Making %r request with URI %r", method, uri)
            res = f('http://' + host + ':' + str(port) + uri)

        logger.debug("Got response code %r", res.status_code)


def load_test(host, port, n_procs, m_reqs):
    logger = logging.getLogger("LoadTest")
    logger.info("Creating %r processes", n_procs)

    workers = []
    for i in range(n_procs):
        worker = Process(target=make_requests, args=(host, port, m_reqs))
        worker.start()
        workers.append(worker)

    logger.info("Joining workers")
    for w in workers:
        w.join()

    '''
    logger.info("Creating pool of %r processes", n_procs)
    pool = Pool(processes=n_procs)

    logger.info("Mapping %r*%r requests on the pool", n_procs, m_reqs)
    pool.map(make_requests, [(host, port, m_reqs)] * n_procs)

    logger.info("Closing and joining the pool")
    pool.close()
    pool.join()
    '''


if __name__ == '__main__':
    load_test(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
