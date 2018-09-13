import sys, os
from flask import Flask, request, Response, jsonify, json
from flask_api import status
app = Flask(__name__)


def ensure_dir(file_path):
	directory = os.path.dirname(file_path)
	if not os.path.exists(directory):
		os.makedirs(directory)


@app.route('/<origin>/<entity>/<id>', methods=['GET'])
def fetch_file(origin, entity, id):
	path = './' + origin + '/' + entity + '/' + id
	try: 
		file = open(path, 'r')
	except IOError:
		return jsonify(error="Resource '{}' not found.".format(path)), status.HTTP_404_NOT_FOUND
	content = file.read()
	file.close()
	return content, status.HTTP_200_OK


@app.route('/<origin>/<entity>/<id>', methods=['POST'])
def create_file(origin, entity, id):
	path = './' + origin + '/' + entity + '/' + id
	ensure_dir(path)
	file = open(path, 'w+')
	print(json.dumps(request.json))
	file.write(json.dumps(request.json))
	file.close()
	return '', status.HTTP_201_CREATED


if __name__ == '__main__':
	app.run(debug=True, port=int(sys.argv[1]))
