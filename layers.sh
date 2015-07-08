#!/bin/bash

img=$1

cat caffe/models/bvlc_googlenet/deploy.prototxt | grep " name" | awk '{ print $2 }' | tr -d '"' > layers.txt

cat layers.txt | while read layer
do
    lname=`echo $layer | tr '/' '-'`
    python dream.py $img $layer > cout.$img.$lname 2> cerr.$img.$lname
done
