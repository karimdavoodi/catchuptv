FROM ubuntu:20.04
LABEL version="1.0"
LABEL type="chan_net_to_epg"

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    gstreamer1.0-libav              \
    gstreamer1.0-plugins-base       \
    gstreamer1.0-plugins-good       \
    gstreamer1.0-plugins-ugly       \
    gstreamer1.0-plugins-bad        \
    ffmpeg gstreamer1.0-libav       \
    gstreamer1.0-tools              \
    tcpdump                         \
    iputils-ping                    \
    vim curl wget                   \
    postgresql-client-12            \
    python3-psycopg2 python3-pip \
    tzdata                          \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pika
RUN pip3 install redis
COPY mq-test.py  /

CMD [ "/bin/bash", "-c","while true;do sleep 5; echo 'running'; done" ]
