FROM ubuntu:20.04 
LABEL version="1.0"

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3-pip \
    ffmpeg \
    tzdata      \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pika
RUN pip3 install pyinotify
COPY transcoder.py  /

ENV TZ=Asia/Istanbul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

CMD [ "python3", "/transcoder.py" ]
