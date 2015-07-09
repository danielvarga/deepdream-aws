set -e

# Disable camera, we don't have any:
sudo ln /dev/null /dev/raw1394

git clone git@github.com:danielvarga/deepdream-aws.git
cd deepdream-aws
ln -s ~/caffe .
# Get the googlenet model file:
wget http://dl.caffe.berkeleyvision.org/bvlc_googlenet.caffemodel
mv bvlc_googlenet.caffemodel caffe/models/bvlc_googlenet/

# Get some input image:
wget --output-document=daniel.png https://www.gravatar.com/avatar/17d651b2d4092b7810ae23d8d94b8cbd?s=640
convert daniel.png daniel.jpg

# Run:
nohup bash layers.sh daniel.jpg &
