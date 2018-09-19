FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

COPY ./back_end_server/requirements.txt /be/requirements.txt

WORKDIR /be

RUN pip3 install -r requirements.txt

COPY ./back_end_server /be/be_server
COPY ./http_server /be/http_server

ENV CACHE_SIZE 0

ENTRYPOINT [ "python3" ]

CMD [ "-m", "be_server", "front", "5001", "0" ]