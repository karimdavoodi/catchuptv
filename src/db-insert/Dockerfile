FROM ubuntu:20.04
LABEL version="1.0"

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3-psycopg2 python3-pip \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install pika
COPY db-insert.py  /

CMD [ "/usr/bin/python3", "/db-insert.py" ]
