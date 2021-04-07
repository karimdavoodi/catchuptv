#!/bin/sh

PID_FILE=/var/lib/rabbitmq/mnesia/rabbit@`hostname`.pid
# Create Rabbitmq user
( rabbitmqctl wait --timeout 60 $PID_FILE ; \
rabbitmqctl add_user $GB_MQ_USER $GB_MQ_PASS 2>/dev/null ; \
rabbitmqctl set_user_tags $GB_MQ_USER administrator ; \
rabbitmqctl set_permissions -p / $GB_MQ_USER  ".*" ".*" ".*" ; \
echo "*** User '$GB_MQ_USER' with password '$GB_MQ_PASS' completed. ***" ; \
echo "*** Log in the WebUI at port 15672 (example: http:/localhost:15672) ***") &

# $@ is used to pass arguments to the rabbitmq-server command.
# For example if you use it like this: docker run -d rabbitmq arg1 arg2,
# it will be as you run in the container rabbitmq-server arg1 arg2
rabbitmq-server $@
