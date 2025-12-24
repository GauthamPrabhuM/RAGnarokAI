# DocuMind AI Development Guide

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Backend Development](#backend-development)
3. [Frontend Development](#frontend-development)
4. [Testing](#testing)
5. [Deployment](#deployment)
6. [Troubleshooting](#troubleshooting)

## Local Development Setup

### Prerequisites

1. **AWS Account** with the following:
   - AWS CLI configured (`aws configure`)
   - Access to Amazon Bedrock (request in AWS Console)
   - IAM user with appropriate permissions

2. **Required Tools**:
   ```bash
   # Install AWS SAM CLI (macOS)
   brew install aws-sam-cli
   
   # Install Node.js 18+
   brew install node
   
   # Install Python 3.11+
   brew install python@3.11
   ```

3. **Enable Bedrock Model Access**:
   - Go to AWS Console → Amazon Bedrock → Model access
   - Request access to "Claude 3 Haiku" model
   - Wait for approval (usually instant)

## Backend Development

### Project Structure
```
backend/
├── src/
│   ├── handlers/       # Lambda function handlers
│   ├── utils/          # Shared utilities
│   └── requirements.txt
├── template.yaml       # SAM template
└── samconfig.toml      # SAM configuration
```

### Running Locally

```bash
cd backend

# Install dependencies
pip install -r src/requirements.txt

# Start local API
sam local start-api --warm-containers EAGER

# The API will be available at http://localhost:3000
```

### Testing Lambda Functions

```bash
# Test a specific function
sam local invoke UploadFunction --event events/upload.json

# Generate sample events
sam local generate-event apigateway aws-proxy > events/sample.json
```

### Adding New Lambda Functions

1. Create handler in `src/handlers/`
2. Add function definition in `template.yaml`
3. Add API Gateway event mapping
4. Deploy with `sam deploy`

## Frontend Development

### Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env
# Edit .env with your API URL

# Start development server
npm run dev
```

### Building for Production

```bash
npm run build
# Output will be in dist/
```

### Project Structure
```
frontend/
├── src/
│   ├── components/    # Reusable UI components
│   ├── pages/         # Page components
│   ├── services/      # API services
│   ├── types/         # TypeScript types
│   └── App.tsx        # Main app component
├── package.json
└── vite.config.ts
```

## Testing

### Backend Testing

```bash
cd backend

# Run unit tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/
```

### Frontend Testing

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm run test:coverage
```

## Deployment

### First-Time Deployment

```bash
# Make deploy script executable
chmod +x scripts/deploy.sh

# Deploy (default: dev environment)
./scripts/deploy.sh dev

# Deploy to production
./scripts/deploy.sh prod
```

### Manual Deployment

```bash
# Backend
cd backend
sam build
sam deploy --guided

# Frontend (after backend is deployed)
cd frontend
npm install
npm run build
aws s3 sync dist/ s3://YOUR-FRONTEND-BUCKET
```

### Updating the Stack

```bash
# Just run deploy again
./scripts/deploy.sh dev
```

## Troubleshooting

### Common Issues

#### "Access Denied" when using Bedrock

1. Ensure you've requested model access in AWS Console
2. Check IAM permissions include `bedrock:InvokeModel`
3. Verify the model ID is correct in `template.yaml`

#### Lambda Timeout

Increase timeout in `template.yaml`:
```yaml
Globals:
  Function:
    Timeout: 60  # Increase from 30
```

#### CORS Errors

Ensure API Gateway CORS is configured:
```yaml
Cors:
  AllowMethods: "'*'"
  AllowHeaders: "'*'"
  AllowOrigin: "'*'"
```

#### S3 Upload Fails

1. Check bucket CORS configuration
2. Verify presigned URL hasn't expired
3. Ensure content-type matches

### Viewing Logs

```bash
# View Lambda logs
sam logs -n UploadFunction --stack-name documind-ai-dev --tail

# View all CloudWatch logs
aws logs tail /aws/lambda/DocuMind-Upload-dev --follow
```

### Cleanup

To remove all resources:

```bash
chmod +x scripts/cleanup.sh
./scripts/cleanup.sh dev
```

## Architecture Decisions

### Why These Services?

| Service | Reason |
|---------|--------|
| **Lambda** | Serverless, scales to zero, pay-per-use |
| **S3** | Durable document storage, presigned URLs |
| **DynamoDB** | Serverless NoSQL, fast lookups |
| **Bedrock** | Managed LLM, no model hosting needed |
| **Textract** | High-accuracy OCR, handles complex layouts |
| **API Gateway** | REST API, throttling, CORS handling |

### Why Python for Backend?

- Excellent AWS SDK (boto3)
- Great for AI/ML workloads
- Fast Lambda cold starts with Python 3.11

### Why React + Vite for Frontend?

- Fast development experience
- Modern tooling
- Easy to deploy as static site
