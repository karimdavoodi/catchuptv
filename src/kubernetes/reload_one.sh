#!/bin/bash
IMAGE=$1
kubectl delete -f deployments/$IMAGE.yaml
kubectl create -f deployments/$IMAGE.yaml
