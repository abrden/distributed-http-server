# distributed-http-server

## Dockerize Back End
```
sudo docker build -f back_end_server/Dockerfile -t distribute-http-server-be:latest .
sudo docker run -p 5001:5000 distribute-http-server-be
```

## cURL Examples
```
curl -X GET http://0.0.0.0:5001
```
