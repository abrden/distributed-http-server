FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

COPY ./back-end-server/requirements.txt /be/requirements.txt

WORKDIR /be

RUN pip3 install -r requirements.txt

COPY ./back-end-server /be/server
COPY ./http-server /be/http-server

ENTRYPOINT [ "python3" ]

CMD [ "server/be-server.py", "0.0.0.0", "5000" ]