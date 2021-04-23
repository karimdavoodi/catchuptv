FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN pip3 install pymongo

COPY src/condent_store/cs-offline-play/app/main.py  /app
COPY src/libs/python/util.py  /app/

