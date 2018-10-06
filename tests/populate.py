import sys
import logging
import random

logging.basicConfig(level=logging.INFO)

from request import post

origins = ['netflix', 'spotify', 'almundo', 'pandora', 'hulu']
resources = ['movies', 'series', 'songs', 'albums', 'artists', 'users']


def generate_random_content():
    jsons = ["{'hello':'world'}", "{'hola':'mundo'}", "{'bonjour':'le monde'}", "{'ciao':'mondo'}"]
    return random.choice(jsons)


def populate(host, port):
    logger = logging.getLogger("Populator")
    for i in range(1, 10):
        for origin in origins:
            for resource in resources:
                uri = '/' + origin + '/' + resource + '/' + str(i)
                content = generate_random_content()
                res = post('http://' + host + ':' + str(port) + uri, content)
                logger.info("Made POST request with URI %r and content %r - Response %r", uri, content, res.status_code)


if __name__ == '__main__':
    populate(sys.argv[1], int(sys.argv[2]))
