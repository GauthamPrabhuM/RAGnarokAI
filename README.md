<p align="center">
  <img src="https://img.icons8.com/color/200/lightning-bolt--v1.png" alt="RAGnarokAI Logo" width="120"/>
</p>

<h1 align="center">⚡ RAGnarokAI</h1>

<p align="center">
  <strong>Unleash the Power of AI on Your Documents</strong>
</p>

<p align="center">
  <em>The End of Manual Document Analysis</em>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-deployment">Deployment</a> •
  <a href="#-api-reference">API</a> •
  <a href="#-contributing">Contributing</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/AWS-Serverless-FF9900?style=for-the-badge&logo=amazonaws" alt="AWS Serverless"/>
  <img src="https://img.shields.io/badge/Amazon-Bedrock-232F3E?style=for-the-badge&logo=amazonaws" alt="Amazon Bedrock"/>
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react" alt="React 18"/>
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11"/>
  <img src="https://img.shields.io/badge/TypeScript-5.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License"/>
</p>

---

## 🌟 What is RAGnarokAI?

**RAGnarokAI** is a serverless AI-powered document intelligence platform that brings the **end times to manual document analysis**! 

Upload any document and instantly:

- 🔍 **Extract text** with enterprise-grade OCR powered by Amazon Textract
- 📝 **Generate summaries** using Claude 3 AI via Amazon Bedrock
- 💬 **Ask questions** and get instant answers with RAG (Retrieval-Augmented Generation)
- 🏷️ **Extract entities** like names, dates, locations, and organizations

Built entirely on **AWS serverless architecture**, it scales from zero to millions of documents while keeping costs minimal.

---

## ✨ Features

| Feature | Description | AWS Service |
|---------|-------------|-------------|
| 📄 **Smart Upload** | Drag & drop PDFs, images, or text files | S3 + Lambda |
| 🔍 **Text Extraction** | High-accuracy OCR for any document type | Amazon Textract |
| 📝 **AI Summarization** | Intelligent summaries in seconds | Amazon Bedrock (Claude 3) |
| 💬 **Document Q&A** | Ask questions, get accurate answers with RAG | Amazon Bedrock |
| 🏷️ **Entity Extraction** | Auto-detect people, orgs, dates, locations | Amazon Bedrock |
| ⚡ **Serverless** | Scales automatically, pay only for what you use | Lambda + API Gateway |
| 🔐 **Secure** | Encrypted storage, IAM-based access | S3 + DynamoDB |

---

## 🏗️ Architecture

\`\`\`
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 FRONTEND                                     │
│  ┌─────────────────┐    ┌──────────────────┐    ┌───────────────────────┐   │
│  │   React + Vite  │───▶│    CloudFront    │───▶│     S3 (Static)       │   │
│  │   Tailwind CSS  │    │       CDN        │    │      Hosting          │   │
│  └─────────────────┘    └──────────────────┘    └───────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 BACKEND                                      │
│  ┌─────────────────┐    ┌──────────────────┐    ┌───────────────────────┐   │
│  │   API Gateway   │───▶│  Lambda Functions │───▶│   Amazon Bedrock      │   │
│  │    (REST)       │    │    (Python 3.11)  │    │   (Claude 3 Haiku)    │   │
│  └─────────────────┘    └──────────────────┘    └───────────────────────┘   │
│                                  │                                           │
│                    ┌─────────────┼─────────────┐                            │
│                    ▼             ▼             ▼                            │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────────────┐      │
│  │    S3 Bucket    │  │  Amazon Textract │  │      DynamoDB         │      │
│  │   (Documents)   │  │      (OCR)       │  │   (Document Meta)     │      │
│  └─────────────────┘  └──────────────────┘  └───────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
\`\`\`

---

## 🚀 Quick Start

### Prerequisites

- ✅ AWS Account with Bedrock access
- ✅ AWS CLI configured (\`aws configure\`)
- ✅ Node.js 18+ and Python 3.11+
- ✅ AWS SAM CLI

\`\`\`bash
# macOS installation
brew install aws-sam-cli node python@3.11
\`\`\`

### Enable Amazon Bedrock

1. Go to **AWS Console** → **Amazon Bedrock** → **Model access**
2. Request access to **Claude 3 Haiku**
3. Wait for approval (usually instant)

### Deploy in One Command

\`\`\`bash
# Clone the repository
git clone https://github.com/GauthamPrabhuM/RAGnarokAI.git
cd RAGnarokAI

# Make deploy script executable
chmod +x scripts/deploy.sh

# Deploy to AWS
./scripts/deploy.sh dev
\`\`\`

🎉 **That's it!** The script will output your application URLs.

---

## 📖 Deployment

### One-Command Deployment

\`\`\`bash
./scripts/deploy.sh dev     # Development environment
./scripts/deploy.sh staging # Staging environment  
./scripts/deploy.sh prod    # Production environment
\`\`\`

### Manual Deployment

#### Backend
\`\`\`bash
cd backend
sam build
sam deploy --guided
\`\`\`

#### Frontend
\`\`\`bash
cd frontend
npm install
echo "VITE_API_URL=YOUR_API_URL" > .env
npm run build
aws s3 sync dist/ s3://YOUR-FRONTEND-BUCKET
\`\`\`

### Cleanup
\`\`\`bash
./scripts/cleanup.sh dev  # ⚠️ Removes all resources
\`\`\`

---

## 🔌 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| \`GET\` | \`/upload\` | Get presigned upload URL |
| \`POST\` | \`/upload\` | Confirm document upload |
| \`GET\` | \`/documents\` | List all documents |
| \`GET\` | \`/documents/{id}\` | Get document details |
| \`DELETE\` | \`/documents/{id}\` | Delete document |
| \`POST\` | \`/documents/{id}/extract\` | Extract text (OCR) |
| \`GET\` | \`/documents/{id}/summarize\` | Generate AI summary |
| \`POST\` | \`/documents/{id}/query\` | Ask questions (RAG) |

### Example: Ask a Question

\`\`\`bash
curl -X POST https://API_URL/documents/DOC_ID/query \\
  -H "Content-Type: application/json" \\
  -H "X-User-Id: user-123" \\
  -d '{"question": "What are the key findings in this document?"}'
\`\`\`

**Response:**
\`\`\`json
{
  "documentId": "abc-123",
  "question": "What are the key findings in this document?",
  "answer": "The document outlines three key findings: 1) Market growth of 25%...",
  "confidence": "high"
}
\`\`\`

📚 [Full API Documentation](docs/API.md)

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.11** | Lambda runtime |
| **AWS SAM** | Infrastructure as Code |
| **Amazon Bedrock** | AI/LLM (Claude 3 Haiku) |
| **Amazon Textract** | Document OCR |
| **Amazon DynamoDB** | Metadata storage |
| **Amazon S3** | Document storage |
| **API Gateway** | REST API |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI framework |
| **TypeScript** | Type safety |
| **Vite** | Build tool |
| **Tailwind CSS** | Styling |
| **Lucide React** | Icons |
| **React Router** | Navigation |

---

## 📁 Project Structure

\`\`\`
RAGnarokAI/
├── �� backend/
│   ├── 📂 src/
│   │   ├── 📂 handlers/          # Lambda functions
│   │   │   ├── upload.py         # Document upload handling
│   │   │   ├── extract.py        # Text extraction (Textract)
│   │   │   ├── summarize.py      # AI summarization (Bedrock)
│   │   │   ├── query.py          # Q&A with RAG (Bedrock)
│   │   │   └── documents.py      # CRUD operations
│   │   └── 📂 utils/             # Shared utilities
│   │       ├── bedrock.py        # Bedrock client
│   │       ├── textract.py       # Textract client
│   │       └── dynamodb.py       # DynamoDB client
│   ├── template.yaml             # SAM template (IaC)
│   └── samconfig.toml            # SAM configuration
│
├── 📂 frontend/
│   ├── 📂 src/
│   │   ├── 📂 components/        # Reusable UI components
│   │   ├── 📂 pages/             # Page components
│   │   ├── 📂 services/          # API client
│   │   └── 📂 types/             # TypeScript types
│   ├── package.json
│   └── tailwind.config.js
│
├── 📂 docs/                      # Documentation
│   ├── API.md                    # API reference
│   └── DEVELOPMENT.md            # Dev guide
│
├── 📂 scripts/                   # Deployment scripts
│   ├── deploy.sh                 # One-click deploy
│   └── cleanup.sh                # Resource cleanup
│
├── LICENSE
└── README.md
\`\`\`

---

## 💰 Cost Estimation

This serverless architecture is **extremely cost-effective**:

| Service | Pricing |
|---------|---------|
| **Lambda** | ~\$0.20 per 1M requests |
| **S3** | ~\$0.023 per GB/month |
| **DynamoDB** | Pay per request |
| **Textract** | ~\$1.50 per 1000 pages |
| **Bedrock (Claude 3 Haiku)** | ~\$0.00025 per 1K input tokens |

💵 **Estimated monthly cost for moderate usage: \$5-20**

---

## 🔧 Local Development

### Backend
\`\`\`bash
cd backend
pip install -r src/requirements.txt
sam local start-api
# API available at http://localhost:3000
\`\`\`

### Frontend
\`\`\`bash
cd frontend
npm install
npm run dev
# App available at http://localhost:5173
\`\`\`

📚 [Full Development Guide](docs/DEVELOPMENT.md)

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** your feature branch (\`git checkout -b feature/AmazingFeature\`)
3. **Commit** your changes (\`git commit -m 'Add some AmazingFeature'\`)
4. **Push** to the branch (\`git push origin feature/AmazingFeature\`)
5. **Open** a Pull Request

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

<p align="center">
  <strong>Gautham Prabhu M</strong>
</p>

<p align="center">
  <a href="https://github.com/GauthamPrabhuM">
    <img src="https://img.shields.io/badge/GitHub-GauthamPrabhuM-181717?style=for-the-badge&logo=github" alt="GitHub"/>
  </a>
</p>

---

<p align="center">
  <img src="https://img.icons8.com/color/48/lightning-bolt--v1.png" width="30"/>
</p>

<h3 align="center">RAGnarokAI</h3>

<p align="center">
  <strong>The End of Manual Document Analysis</strong>
</p>

<p align="center">
  <em>Built with ❤️ and ☕ | Powered by AWS</em>
</p>

<p align="center">
  ⭐ <strong>Star this repo if you found it helpful!</strong> ⭐
</p>
