# distributed-http-server

## Front End
```
python3 -m front_end_server 127.0.0.1 5000 127.0.0.1 5001 1
```

## Dockerize Front End
```
sudo docker build -f front_end_server/Dockerfile -t distribute-http-server-fe:latest .
sudo docker run -p 5000:5000 -p 5001:5001 distribute-http-server-fe
```

## Back End
```
python3 -m back_end_server 127.0.0.1 5001 0
```

## Dockerize Back End
```
sudo docker build -f back_end_server/Dockerfile -t distribute-http-server-be:latest .
sudo docker run -p 5001:5000 distribute-http-server-be
```

## cURL Examples
```
curl -X GET http://0.0.0.0:5001/netflix/movie/2
curl -X POST http://0.0.0.0:5000/netflix/movie/2 -d '{"key1":"value1", "key2":"value2"}'
curl -H 'Expect:' -X POST http://0.0.0.0:5000/netflix/movie/2 -d 'Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur? Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?'
```

## Docker compose
```
sudo docker-compose build && sudo docker-compose up

sudo docker-compose up --scale back=5
```
Don't forget to change the FE dockerfile in order to accept 5 BE's