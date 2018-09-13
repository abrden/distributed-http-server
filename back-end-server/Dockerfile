FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

COPY ./requirements.txt /be/requirements.txt

WORKDIR /be

RUN pip install -r requirements.txt

COPY . /be

ENTRYPOINT [ "python" ]

CMD [ "server.py" ]