FROM ubuntu:20.04
LABEL version="1.0"
LABEL type="db_segment"

#TODO: MUST set in YAML file
ENV MQ_HOST="192.168.1.23"
ENV MQ_USER="karim"
ENV MQ_PASS="31233123"
ENV MQ_EXCHANGE="segment_info"
ENV DB_HOST="localhost"
ENV DB_DATABASE="segment"
ENV DB_USER="postgres"
ENV DB_PASS="31233123"
# docker run -it  -p '3000:3000' \   // for postrest listening
#       -v /home/temp/containers/progresSqlData:/data \
#       db_segment 

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3-psycopg2 python3-pip \
    postgresql-12 \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install pika
COPY db_segment_*  /
COPY postgrest  /
COPY postgrest.conf  /etc/
COPY pg_hba.conf    /etc/postgresql/12/main/
RUN chmod 0640      /etc/postgresql/12/main/pg_hba.conf 
RUN chown postgres:postgres /etc/postgresql/12/main/pg_hba.conf

CMD [ "/db_segment_start.sh" ]
