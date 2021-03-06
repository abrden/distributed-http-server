# distributed-http-server

## Front End
```
python3 -m front_end_server
```

## Logger
```
python3 -m logger
```

## Back End
```
python3 -m back_end_server
```

## Docker Compose
```
sudo docker-compose build && sudo docker-compose up

sudo docker-compose build && sudo docker-compose up --scale back=5
```
Don't forget to change BE_NUM on the docker-compose.yml to match the number on the --scale flag

#### Copy audit log out from docker container
```
sudo docker cp distributed-http-server_logger_1:logger/audit-log .
```

## cURL Examples
```
curl -D - -X GET http://0.0.0.0:5000/netflix/movie/2
curl -D - -X POST http://0.0.0.0:5000/netflix/movie/2 -d '{"key1":"value1", "key2":"value2"}'
curl -D - -X PUT http://0.0.0.0:5000/netflix/movie/2 -d '{"hello":"world", "key3":"value3"}'
curl -D - -X DELETE http://0.0.0.0:5000/netflix/movie/2
```

## Test
```
python3 tests/load_test.py 0.0.0.0 5000 10 50
python3 tests/load_test.py 0.0.0.0 5000 50 1000
```
