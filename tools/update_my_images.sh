#!/bin/bash

eval $(minikube docker-env)
echo "Current image count: `docker images | wc` "
for a in src/condent_store/*; do 
    app=`basename $a`
    echo "Build $app"
    docker build -t $app -f src/condent_store/$app/Dockerfile .
done
