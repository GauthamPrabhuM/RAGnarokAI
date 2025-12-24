#!/bin/bash

# RAGnarokAI - Deployment Script
# This script deploys both backend and frontend

set -e

echo "⚡ RAGnarokAI Deployment Script"
echo "================================"

# Configuration
ENVIRONMENT=${1:-dev}
REGION=${AWS_REGION:-us-east-1}

echo "📋 Configuration:"
echo "   Environment: $ENVIRONMENT"
echo "   Region: $REGION"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

if ! command -v sam &> /dev/null; then
    echo "❌ AWS SAM CLI is not installed. Please install it first."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install it first."
    exit 1
fi

echo "✅ All prerequisites met!"
echo ""

# Deploy Backend
echo "📦 Deploying Backend..."
cd backend

echo "   Building SAM application..."
sam build

echo "   Deploying to AWS..."
sam deploy \
    --stack-name "ragnarokai-$ENVIRONMENT" \
    --parameter-overrides "Environment=$ENVIRONMENT" \
    --capabilities CAPABILITY_IAM \
    --no-confirm-changeset \
    --no-fail-on-empty-changeset

# Get outputs
echo ""
echo "📤 Getting deployment outputs..."
API_URL=$(aws cloudformation describe-stacks \
    --stack-name "ragnarokai-$ENVIRONMENT" \
    --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
    --output text)

FRONTEND_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name "ragnarokai-$ENVIRONMENT" \
    --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" \
    --output text)

FRONTEND_URL=$(aws cloudformation describe-stacks \
    --stack-name "ragnarokai-$ENVIRONMENT" \
    --query "Stacks[0].Outputs[?OutputKey=='FrontendUrl'].OutputValue" \
    --output text)

echo "   API URL: $API_URL"
echo "   Frontend Bucket: $FRONTEND_BUCKET"
echo ""

# Deploy Frontend
echo "🎨 Deploying Frontend..."
cd ../frontend

echo "   Installing dependencies..."
npm install

echo "   Creating environment file..."
echo "VITE_API_URL=$API_URL" > .env

echo "   Building frontend..."
npm run build

echo "   Uploading to S3..."
aws s3 sync dist/ "s3://$FRONTEND_BUCKET" --delete

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "🌐 Your application is live at:"
echo "   Frontend: $FRONTEND_URL"
echo "   API: $API_URL"
echo ""
echo "📚 Next steps:"
echo "   1. Enable Amazon Bedrock model access in AWS Console"
echo "   2. Request access to Claude 3 Haiku model"
echo "   3. Test the application by uploading a document"
