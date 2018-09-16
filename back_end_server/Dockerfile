FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

COPY ./back_end_server/requirements.txt /be/requirements.txt

WORKDIR /be

RUN pip3 install -r requirements.txt

COPY ./back_end_server /be/be_server
COPY ./http_server /be/http_server

ENTRYPOINT [ "python3" ]

CMD [ "-m", "be_server", "0.0.0.0", "5000" ]