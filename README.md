# deepdream-aws

Setting up and running the Deep Dream algorithm on AWS EC2.

Go through the steps of `readme.sh` to create and set up an EC2 instance.
We use Tito Costa's Torch+Caffe EC2 AMI, documented at http://blog.titocosta.com/post/110345699197/public-ec2-ami-with-torch-and-caffe-deep-learning
. Big thanks, Tito!

`setup.sh` is what sets up the algorithm and its inputs on the instance,
at the /home/ubuntu/deepdream-aws directory.
Beware, its last line starts the `layers.sh` script as well,
you'll probably want to comment that line out.

`python dream.py IMAGE.jpg LAYER` runs the algorithm for a given GoogLeNet layer.
The output is `IMAGE.LAYER.jpg`.

`bash layers.sh IMAGE.jpg` runs the Deep Dream algorithm for a given image, for each layer of the neural network.
Images with alpha channel are not allowed.
