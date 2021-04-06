#!/bin/bash
IMAGE=$1
docker build .  --network host -t $IMAGE
minikube cache delete $IMAGE
minikube cache add $IMAGE

