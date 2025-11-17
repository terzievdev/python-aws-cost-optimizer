#!/bin/bash
# user_data.sh - EC2 instance initialization

set -e

# Update system
apt-get update
apt-get upgrade -y

# Install Python and dependencies
apt-get install -y python3-pip python3-venv git

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install
rm -rf aws awscliv2.zip

# Create application directory
mkdir -p /home/ubuntu/cost-optimizer
cd /home/ubuntu/cost-optimizer

# Set permissions
chown -R ubuntu:ubuntu /home/ubuntu/cost-optimizer

echo " EC2 instance initialized! Ready for application deployment."
