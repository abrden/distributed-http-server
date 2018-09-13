FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

COPY ./requirements.txt /fe/requirements.txt

WORKDIR /fe

RUN pip install -r requirements.txt

COPY . /fe

ENV CACHE_SIZE 0

ENTRYPOINT [ "python" ]

CMD [ "server.py", "CACHE_SIZE" ]