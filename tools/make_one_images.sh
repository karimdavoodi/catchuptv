#!/bin/bash
IMAGE=$1
cd /opt/catchuptv/src/$IMAGE
docker build .  --network host -t $IMAGE
minikube cache delete $IMAGE
minikube cache add $IMAGE

