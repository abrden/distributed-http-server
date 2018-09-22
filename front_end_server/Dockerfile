FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

COPY ./front_end_server/requirements.txt /fe/requirements.txt

WORKDIR /fe

RUN pip3 install --upgrade pip setuptools
RUN pip3 install -r requirements.txt

COPY ./front_end_server /fe/fe_server
COPY ./http_server /fe/http_server
COPY ./concurrency /fe/concurrency

ENV BE_NUM 1

ENTRYPOINT [ "python3" ]

CMD [ "-m", "fe_server", "0.0.0.0", "5000", "0.0.0.0", "5001", "1" ]