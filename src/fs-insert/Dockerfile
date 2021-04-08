FROM python:3.8-slim-buster

#FROM ubuntu:20.04
LABEL version="1.0"

RUN pip3 install pika
COPY fs-insert.py /

CMD [ "/usr/bin/python3", "/fs-insert.py" ]
