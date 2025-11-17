#!/bin/bash
# deploy.sh - Deploy Cost Optimizer to EC2

set -e

echo " Deploying AWS Cost Optimizer to EC2..."

# Configuration
KEY_PATH="$HOME/.ssh/trainee-key.pem"
EC2_USER="ubuntu"
EC2_HOST=""  # Will be set after instance creation
INSTANCE_NAME="cost-optimizer-dashboard"
REGION="us-east-1"

# Step 1: Launch EC2 instance
echo " Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id ami-0c7217cdde317cfec \
    --instance-type t2.small \
    --key-name trainee-key \
    --security-group-ids $(aws ec2 describe-security-groups --filters "Name=group-name,Values=default" --query 'SecurityGroups[0].GroupId' --output text) \
    --iam-instance-profile Name=trainee-ec2-s3-role \
    --user-data file://user_data.sh \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME},{Key=Project,Value=CostOptimizer}]" \
    --region $REGION \
    --query 'Instances[0].InstanceId' \
    --output text)

echo " Instance launched: $INSTANCE_ID"
echo " Waiting for instance to be running..."

aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION

# Get public IP
EC2_HOST=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text \
    --region $REGION)

echo " Instance running at: $EC2_HOST"

# Step 2: Configure Security Group for Flask
echo " Configuring security group for port 5000..."
SG_ID=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' \
    --output text \
    --region $REGION)

aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 5000 \
    --cidr 0.0.0.0/0 \
    --region $REGION 2>/dev/null || echo "Port 5000 already open"

# Step 3: Wait for instance to be ready
echo " Waiting for SSH to be ready (2 minutes)..."
sleep 120

# Step 4: Deploy application files
echo " Deploying application files..."

# Create deployment package
tar -czf deploy.tar.gz \
    src/ templates/ static/ data/ \
    requirements.txt config.py \
    --exclude='*.pyc' --exclude='__pycache__'

# Upload via EC2 Instance Connect (since SSH is blocked)
echo " Files packaged. Use EC2 Instance Connect to upload:"
echo ""
echo "1. Go to AWS Console → EC2 → $INSTANCE_ID"
echo "2. Click 'Connect' → 'EC2 Instance Connect'"
echo "3. Upload deploy.tar.gz"
echo "4. Run: tar -xzf deploy.tar.gz && cd python-aws-cost-optimizer"
echo "5. Run: pip3 install -r requirements.txt"
echo "6. Run: python3 src/app.py"
echo ""
echo " Dashboard will be available at: http://$EC2_HOST:5000"
echo ""
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $EC2_HOST"
