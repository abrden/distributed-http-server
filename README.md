# distributed-http-server

## Front End
```
python3 -m front_end_server
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
sudo docker cp distributed-http-server_front_1:fe/audit-log .
```

## cURL Examples
```
curl -X GET http://0.0.0.0:5000/netflix/movie/2
curl -X POST http://0.0.0.0:5000/netflix/movie/2 -d '{"key1":"value1", "key2":"value2"}'
curl -X PUT http://0.0.0.0:5000/netflix/movie/2 -d '{"hello":"world", "key3":"value3"}'
curl -X DELETE http://0.0.0.0:5000/netflix/movie/2
```

