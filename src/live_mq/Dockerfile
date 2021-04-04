FROM rabbitmq:latest
LABEL version="1.0"
LABEL type="live_mq"
# sudo docker run -it -p '15672:15672' -p '5672:5672' -p '25672:25672' live_mq 

ENV RABBITMQ_TTL 30000
ENV RABBITMQ_USER karim
ENV RABBITMQ_PASSWORD 31233123
ENV RABBITMQ_PID_FILE /var/lib/rabbitmq/mnesia/rabbitmq

ADD live_mq_start.sh /live_mq_start.sh
RUN chmod +x /live_mq_start.sh
EXPOSE 15672

CMD ["/live_mq_start.sh"]
