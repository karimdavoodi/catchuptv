#!/bin/bash
CUR=`pwd`
for dir in chan-net-to-epg gb-mq db-epg db-trim db-segment; do
    cd ../$dir
    echo "###################################################  Build $dir"
    docker build .  --network host -t localhost:32000/$dir:registry

    echo "Push $dir"
    docker push localhost:32000/$dir
done
cd $CUR


