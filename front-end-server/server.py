import sys
from flask import Flask, request, Response, json
from flask_api import status
app = Flask(__name__)

from cache.ThreadSafeLRUCache import ThreadSafeLRUCache
from middleware import fetchFromServer, saveInServer

cache = ThreadSafeLRUCache(int(sys.argv[1]))


@app.route('/<origin>/<entity>/<id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def hello_name(origin, entity, id):
	path = '/' + origin + '/' + entity + '/' + id
	
	if request.method == 'GET':
		if cache.hasEntry(path):
			cached_response = cache.getEntry(path)
			return Response(cached_response, status=status.HTTP_200_OK, mimetype='application/json')
		else:
			be_response, be_status = fetchFromServer(origin, entity, id)
			if be_status != status.HTTP_200_OK:
				return Response(be_response, status=status.HTTP_404_NOT_FOUND, mimetype='application/json')
			cache.loadEntry(path, be_response)
			return Response(be_response, status=status.HTTP_200_OK, mimetype='application/json')
			
	elif request.method == 'POST':
		be_response, be_status = saveInServer(origin, entity, id, json.dumps(request.json))
		cache.loadEntry(path, json.dumps(request.json))
		return Response(be_response, status=be_status, mimetype='application/json')
		
	elif request.method == 'PUT':
		# TODO
		return status.HTTP_501_NOT_IMPLEMENTED
	elif request.method == 'DELETE':
		# TODO
		return status.HTTP_501_NOT_IMPLEMENTED


if __name__ == '__main__':
	app.run(
		debug=True,
		threaded=True,
		host='0.0.0.0' if len(sys.argv) < 2 else '127.0.0.1'
	)
