FROM python:3.9-slim
LABEL version="1.0"

RUN pip3 install pika
RUN pip3 install psycopg2-binary
COPY epg-insert.py  /

CMD [ "python3", "/epg-insert.py" ]
