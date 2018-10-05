FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

WORKDIR /logger

COPY ./logger /logger/audit_logger
COPY ./connectivity /logger/connectivity

ENTRYPOINT [ "python3" ]

CMD [ "-m", "audit_logger" ]