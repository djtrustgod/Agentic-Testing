#!/bin/bash
set -e

AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="123456789012"
ECR_REPO="nodejs-app"
IMAGE_TAG="${GITHUB_SHA:-latest}"

# Authenticate with ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build and push image
docker build -t $ECR_REPO:$IMAGE_TAG . 
docker tag $ECR_REPO:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:$IMAGE_TAG
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws. com/$ECR_REPO: $IMAGE_TAG

# Update ECS service (forces new deployment)
aws ecs update-service \
  --cluster nodejs-app-cluster \
  --service nodejs-app-service \
  --force-new-deployment \
  --region $AWS_REGION

echo "Deployment initiated.  Monitor at: https://console.aws.amazon.com/ecs"