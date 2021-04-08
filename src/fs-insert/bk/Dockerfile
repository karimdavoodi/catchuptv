FROM ubuntu:20.04
LABEL version="1.0"
LABEL type="db_segment"

#TODO: MUST set in YAML file
ENV MQ_SRC_HOST="192.168.1.23"
ENV MQ_SRC_USER="karim"
ENV MQ_SRC_PASS="31233123"
ENV MQ_SRC_QUEUE="segment"
ENV MQ_CACHE_HOST="192.168.1.23"
ENV MQ_CACHE_USER="karim"
ENV MQ_CACHE_PASS="31233123"
ENV MQ_CACHE_QUEUE="segment"

# docker run -it  -p '3000:3000' \   // for postrest listening
#       -v /home/temp/containers/progresSqlData:/data \
#       db_segment 

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3-pip \
    nginx \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install pika
COPY fs_segment_*  /
COPY nginx.conf /etc/nginx/sites-enabled/default

CMD [ "/fs_segment_start.sh" ]
