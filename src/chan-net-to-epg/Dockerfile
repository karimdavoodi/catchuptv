FROM ubuntu:20.04
LABEL version="1.0"
LABEL type="chan_net_to_epg"

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    libboost-log1.71.0              \
    libboost-chrono1.71.0           \
    gstreamer1.0-libav              \
    libgstreamer-plugins-bad1.0-0   \
    libgstreamer-plugins-good1.0-0  \
    libgstreamer-plugins-base1.0-0  \
    libgstreamer-gl1.0-0            \
    librabbitmq4                    \
    tzdata                          \
    && rm -rf /var/lib/apt/lists/*


COPY chan_net_to_epg  /

ENV TZ=Asia/Istanbul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

CMD [ "/chan_net_to_epg" ]
