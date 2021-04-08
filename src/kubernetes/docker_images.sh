#!/bin/bash
# External containers
for m in \
nginx:1.19 \
elasticsearch:6.8.4 \
postgres:13.2 \
postgrest/postgrest \
rabbitmq:3.8 \
alpine:3.6 \
docker.elastic.co/beats/filebeat:6.8.4 \
docker.elastic.co/kibana/kibana-oss:6.8.4 \
docker.elastic.co/logstash/logstash:6.3.0; 
do 
    echo "IMAGE: $m"
    docker pull $m
    minikube cache add $m 
done
