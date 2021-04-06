#!/bin/bash
CUR=`pwd`
#minikube cache reload
for dir in chan-net-to-epg gb-mq db-epg db-trim db-segment; do
    echo "###################################################  Build $dir"
    cd ../$dir
    docker build .  --network host -t $dir
    minikube cache delete $dir
    minikube cache add $dir
done
cd $CUR
# LOCAL REGISTRY
# docker run -d -p 5000:5000 --restart=always --name registry registry:2

