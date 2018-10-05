import requests


def get(url, content=None):
    return requests.get(url, headers={'Connection': 'close'})


def post(url, content):
    return requests.post(url, data=content, headers={'Connection': 'close'})


def put(url, content):
    return requests.put(url, data=content, headers={'Connection': 'close'})


def delete(url, content=None):
    return requests.delete(url, headers={'Connection': 'close'}, data="a")  # FIXME Hangs if I dont send content