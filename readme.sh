open https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#LaunchInstanceWizard:ami=ami-ffba7b94
# pick g2.2xlarge
# Request Spot Instances
# Availability Zone: whichever is cheapest
# Maximum price $1.
# Next: Add Storage. Default 60GB is fine.
# Next: Tag. Name:reuse-caffe-test2 is fine.
# Next: Configure Security Group. Default ssh-from-everywhere is fine.
# Launch.
# Choose an existing key pair: reuse-elasticsearch.
# Wait until fulfilled. Click on instance. Check public DNS.

dns=ec2-54-158-172-169.compute-1.amazonaws.com

ssh -i ~/.ssh/reuse-elasticsearch.pem ubuntu@$dns wget https://raw.githubusercontent.com/danielvarga/deepdream-aws/master/setup.sh
ssh -i ~/.ssh/reuse-elasticsearch.pem ubuntu@$dns bash setup.sh
# ...wait some, and then:
scp -i ~/.ssh/reuse-elasticsearch.pem ubuntu@$dns:./deepdream-aws/daniel.inception_3a-3x3.jpg .
