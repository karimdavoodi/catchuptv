FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
RUN pip install redis

COPY src/condent_store/cs-live-cache-play/app/main.py  /app
COPY src/libs/python/util.py  /app/

