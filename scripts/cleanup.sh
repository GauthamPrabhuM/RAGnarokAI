#!/bin/bash

# RAGnarokAI - Cleanup Script
# Removes all deployed resources

set -e

echo "🧹 RAGnarokAI Cleanup Script"
echo "=============================="

ENVIRONMENT=${1:-dev}
STACK_NAME="ragnarokai-$ENVIRONMENT"

echo "⚠️  This will delete the following stack: $STACK_NAME"
echo "⚠️  All documents and data will be permanently deleted!"
echo ""
read -p "Are you sure you want to continue? (y/N): " confirm

if [[ $confirm != [yY] ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "📦 Getting S3 buckets..."

# Get bucket names
DOCUMENTS_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='DocumentsBucketName'].OutputValue" \
    --output text 2>/dev/null || echo "")

FRONTEND_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" \
    --output text 2>/dev/null || echo "")

# Empty S3 buckets (required before deletion)
if [ ! -z "$DOCUMENTS_BUCKET" ] && [ "$DOCUMENTS_BUCKET" != "None" ]; then
    echo "🗑️  Emptying documents bucket: $DOCUMENTS_BUCKET"
    aws s3 rm "s3://$DOCUMENTS_BUCKET" --recursive || true
fi

if [ ! -z "$FRONTEND_BUCKET" ] && [ "$FRONTEND_BUCKET" != "None" ]; then
    echo "🗑️  Emptying frontend bucket: $FRONTEND_BUCKET"
    aws s3 rm "s3://$FRONTEND_BUCKET" --recursive || true
fi

# Delete CloudFormation stack
echo ""
echo "🗑️  Deleting CloudFormation stack..."
aws cloudformation delete-stack --stack-name "$STACK_NAME"

echo "⏳ Waiting for stack deletion..."
aws cloudformation wait stack-delete-complete --stack-name "$STACK_NAME"

echo ""
echo "✅ Cleanup complete! All resources have been deleted."
