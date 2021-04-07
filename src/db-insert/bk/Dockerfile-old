FROM ubuntu:20.04
LABEL version="1.0"
LABEL type="db_epg"

# docker run -it  -p '3000:3000' \   // for postrest listening
#       -v /home/temp/containers/progresSqlData:/data \
#       db_epg 

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3-psycopg2 python3-pip \
    postgresql-12 \
    tzdata       \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install pika
COPY db_epg_*  /
COPY postgrest  /
COPY postgrest.conf  /etc/
COPY pg_hba.conf    /etc/postgresql/12/main/
RUN chmod 0640      /etc/postgresql/12/main/pg_hba.conf 
RUN chown postgres:postgres /etc/postgresql/12/main/pg_hba.conf

ENV TZ=Asia/Istanbul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

CMD [ "/db_epg_start.sh" ]
