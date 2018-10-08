from multiprocessing import Pool
import sys
import os
import random
import logging
import time

from request import get, post, put, delete

logging.basicConfig(level=logging.INFO)


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
            ti = time.time()
            res = f('http://' + host + ':' + str(port) + uri, content)
            tf = time.time()
            logger.info("Made %r request with URI %r and content %r - Got response code %r in %r secs", method, uri, content, res.status_code, tf - ti)
        else:
            logger.debug("Making %r request with URI %r", method, uri)
            ti = time.time()
            res = f('http://' + host + ':' + str(port) + uri)
            tf = time.time()
            logger.info("Made %r request with URI %r - Got response code %r in %r secs", method, uri, res.status_code, tf - ti)


def load_test(host, port, n_procs, m_reqs):
    logger = logging.getLogger("LoadTest")

    logger.info("Creating pool of %r processes", n_procs)
    pool = Pool(processes=n_procs)

    logger.info("Applying %r*%r requests on the pool", n_procs, m_reqs)
    for _ in range(n_procs):
        pool.apply_async(make_requests, (host, port, m_reqs))

    logger.info("Closing and joining the pool")
    pool.close()
    pool.join()


if __name__ == '__main__':
    load_test(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
