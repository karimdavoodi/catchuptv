FROM ubuntu:20.04
LABEL version="1.0"
LABEL type="db_trim"

# docker run -it  -p '80:80' \   // for postrest listening
#       -v /home/temp/containers/progresSqlData:/data \
#       db_trim 

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    postgresql-12 \
    && rm -rf /var/lib/apt/lists/*
COPY db_trim_*  /
COPY postgrest  /
COPY postgrest.conf  /etc/
COPY pg_hba.conf    /etc/postgresql/12/main/
RUN chmod 0640      /etc/postgresql/12/main/pg_hba.conf 
RUN chown postgres:postgres /etc/postgresql/12/main/pg_hba.conf

CMD [ "/db_trim_start.sh" ]
