FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

COPY ./requirements.txt /fe/requirements.txt

WORKDIR /fe

RUN pip3 install -r requirements.txt

COPY . /fe

ENV CACHE_SIZE 0

ENTRYPOINT [ "python3" ]

CMD [ "server.py", "0" ]