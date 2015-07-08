set -e

git clone git@github.com:danielvarga/deepdream-aws.git
cd deepdream-aws
ln -s ~/caffe .
wget http://dl.caffe.berkeleyvision.org/bvlc_googlenet.caffemodel
mv bvlc_googlenet.caffemodel caffe/models/bvlc_googlenet/

wget --output-document=joseroca.png http://0103.static.prezi.com.s3.amazonaws.com/media/3/4/6/50b6e9d49686c9ba30dfbfe7ce434c4652fd4.png
convert joseroca.png joseroca.jpg

nohup bash layers.sh &
