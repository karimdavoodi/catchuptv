FROM rabbitmq:latest
LABEL version="1.0"
LABEL type="gb-mq"
# sudo docker run -it -p '15672:15672' -p '5672:5672' -p '25672:25672' gb_mq 

COPY gb_mq_start.sh /
RUN chmod +x /gb_mq_start.sh

CMD ["/gb_mq_start.sh"]
