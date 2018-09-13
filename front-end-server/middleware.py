import requests

SERVERS = 3

baseurls = [
	'http://127.0.0.1:5001',
	'http://127.0.0.1:5002',
	'http://127.0.0.1:5003'
]


def serverNum(origin):
	return hash(origin) % SERVERS


def fetchFromServer(origin, entity, id):
	be_num = serverNum(origin)
	url = baseurls[0] + '/' + origin + '/' + entity + '/' + id
	response = requests.get(url)
	return response.text, response.status_code


def saveInServer(origin, entity, id, data):
	be_num = serverNum(origin)
	url = baseurls[0] + '/' + origin + '/' + entity + '/' + id
	response = requests.post(url, data=data)
	return response.text, response.status_code
