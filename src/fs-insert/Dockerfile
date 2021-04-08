FROM python:3.9-slim
LABEL version="1.0"

RUN pip3 install pika
COPY fs-insert.py /

CMD [ "python3", "/fs-insert.py" ]
