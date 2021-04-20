FROM python:3.9-slim
LABEL version="1.0"

RUN pip3 install pika               # for RabbitMQ 
RUN pip3 install redis              # for Redis
RUN pip3 install pymongo            # for MongoDB

COPY src/condent_store/cs-mq-to-fs-db-cache/app/cs-mq-to-fs-db-cache.py   /app/

COPY src/libs/python/rabbitmq.py  /app/
COPY src/libs/python/util.py  /app/

CMD [ "python3", "/app/cs-mq-to-fs-db-cache.py" ]
