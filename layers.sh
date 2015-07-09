#!/bin/bash

img=$1

# relu layers are calculated in-place, so we can't use them.
cat caffe/models/bvlc_googlenet/deploy.prototxt | grep " name" | awk '{ print $2 }' | tr -d '"' | grep -v relu > layers.txt

cat layers.txt | while read layer
do
    lname=`echo $layer | tr '/' '-'`
    python dream.py $img $layer > cout.$img.$lname 2> cerr.$img.$lname
done
