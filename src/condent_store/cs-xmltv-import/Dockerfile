FROM python:3.9-slim
LABEL version="1.0"

RUN pip3 install pymongo

COPY src/condent_store/cs-xmltv-import/app/xmltv_import.py   /app/

COPY src/libs/python/util.py  /app/

CMD [ "python3", "/app/xmltv_import.py" ]
