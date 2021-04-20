FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
RUN pip3 install psycopg2-binary

COPY src/condent_store/cs-live-cache-play/app/main.py  /app
COPY src/libs/python/util.py  /app/
COPY src/libs/python/postgresql.py  /app/

