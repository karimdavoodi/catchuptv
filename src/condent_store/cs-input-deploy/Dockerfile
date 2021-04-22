FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN pip3  install requests

COPY src/condent_store/cs-input-deploy/app/main.py  /app
COPY src/condent_store/cs-input-deploy/app/deploy.py  /app
COPY src/libs/python/util.py  /app/

