FROM ubuntu:20.04
LABEL version="1.0"
LABEL type="db_trim"

#TODO: MUST set in YAML file
ENV DB_HOST="localhost"
ENV DB_DATABASE="trim"
ENV DB_USER="postgres"
ENV DB_PASS="31233123"
# docker run -it  -p '3000:3000' \   // for postrest listening
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
