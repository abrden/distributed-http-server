FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

COPY ./requirements.txt /be/requirements.txt

WORKDIR /be

RUN pip3 install -r requirements.txt

COPY . /be

ENTRYPOINT [ "python3" ]

CMD [ "be-server.py" ]