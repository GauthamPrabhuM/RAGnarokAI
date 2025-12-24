# API Reference

## Base URL

```
https://{api-id}.execute-api.{region}.amazonaws.com/{stage}
```

## Authentication

Currently uses a simple `X-User-Id` header for user identification. For production, integrate with Amazon Cognito.

```http
X-User-Id: user-123
```

---

## Endpoints

### Upload

#### Get Presigned Upload URL

```http
GET /upload?filename={filename}&contentType={contentType}
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| filename | string | Yes | Original filename |
| contentType | string | No | MIME type (default: application/pdf) |

**Response:**
```json
{
  "uploadUrl": "https://s3.amazonaws.com/...",
  "documentId": "uuid-string",
  "s3Key": "documents/user-id/date/doc-id/filename.pdf",
  "expiresIn": 3600
}
```

#### Confirm Upload

```http
POST /upload
```

**Request Body:**
```json
{
  "documentId": "uuid-string",
  "s3Key": "documents/...",
  "filename": "document.pdf",
  "contentType": "application/pdf",
  "fileSize": 1024000
}
```

**Response:**
```json
{
  "message": "Document uploaded successfully",
  "document": {
    "documentId": "uuid-string",
    "userId": "user-123",
    "filename": "document.pdf",
    "status": "UPLOADED",
    "createdAt": "2024-01-15T10:30:00Z"
  }
}
```

---

### Documents

#### List Documents

```http
GET /documents?limit={limit}
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| limit | number | No | Max documents to return (default: 50) |

**Response:**
```json
{
  "documents": [
    {
      "documentId": "uuid-string",
      "filename": "document.pdf",
      "status": "COMPLETED",
      "createdAt": "2024-01-15T10:30:00Z",
      "wordCount": 1500
    }
  ],
  "count": 1
}
```

#### Get Document

```http
GET /documents/{documentId}?includeText={bool}&includeHistory={bool}
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| includeText | boolean | Include extracted text |
| includeHistory | boolean | Include Q&A history |

**Response:**
```json
{
  "document": {
    "documentId": "uuid-string",
    "filename": "document.pdf",
    "status": "COMPLETED",
    "extractedText": "Full document text...",
    "summary": "Document summary...",
    "downloadUrl": "https://s3.amazonaws.com/...",
    "queryHistory": [
      {
        "question": "What is the main topic?",
        "answer": "The main topic is...",
        "timestamp": "2024-01-15T11:00:00Z"
      }
    ]
  }
}
```

#### Delete Document

```http
DELETE /documents/{documentId}
```

**Response:**
```json
{
  "message": "Document deleted successfully",
  "documentId": "uuid-string"
}
```

---

### Text Extraction

#### Extract Text

```http
POST /documents/{documentId}/extract
```

**Response:**
```json
{
  "documentId": "uuid-string",
  "text": "Extracted document text...",
  "wordCount": 1500,
  "confidence": 98.5,
  "cached": false
}
```

---

### Summarization

#### Get Summary

```http
GET /documents/{documentId}/summarize?entities={bool}&questions={bool}&maxLength={number}
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| entities | boolean | Include extracted entities |
| questions | boolean | Include suggested questions |
| maxLength | number | Max summary length (default: 500) |

**Response:**
```json
{
  "documentId": "uuid-string",
  "summary": "This document discusses...",
  "wordCount": 1500,
  "cached": false,
  "entities": {
    "people": ["John Smith"],
    "organizations": ["Acme Corp"],
    "dates": ["January 15, 2024"],
    "locations": ["New York"]
  },
  "suggestedQuestions": [
    "What are the key findings?",
    "Who are the main stakeholders?"
  ]
}
```

---

### Q&A

#### Ask Question

```http
POST /documents/{documentId}/query
```

**Request Body:**
```json
{
  "question": "What is the main conclusion?"
}
```

**Response:**
```json
{
  "documentId": "uuid-string",
  "question": "What is the main conclusion?",
  "answer": "The main conclusion is that...",
  "confidence": "high"
}
```

**Confidence Levels:**
- `high`: Answer clearly found in document
- `medium`: Answer inferred from document
- `low`: Answer not found or uncertain

---

## Error Responses

All errors follow this format:

```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

### Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 403 | Forbidden |
| 404 | Not Found |
| 405 | Method Not Allowed |
| 500 | Internal Server Error |

---

## Rate Limits

API Gateway default limits:
- 10,000 requests per second
- 5,000 concurrent requests

Adjust in `template.yaml` if needed.

---

## SDK Examples

### Python

```python
import requests

API_URL = "https://xxx.execute-api.us-east-1.amazonaws.com/dev"
headers = {"X-User-Id": "user-123"}

# Upload document
response = requests.get(
    f"{API_URL}/upload",
    params={"filename": "doc.pdf", "contentType": "application/pdf"},
    headers=headers
)
upload_info = response.json()

# Upload to S3
with open("doc.pdf", "rb") as f:
    requests.put(upload_info["uploadUrl"], data=f)

# Confirm upload
requests.post(
    f"{API_URL}/upload",
    json={
        "documentId": upload_info["documentId"],
        "s3Key": upload_info["s3Key"],
        "filename": "doc.pdf",
        "contentType": "application/pdf",
        "fileSize": 1024000
    },
    headers=headers
)

# Ask question
response = requests.post(
    f"{API_URL}/documents/{upload_info['documentId']}/query",
    json={"question": "What is this document about?"},
    headers=headers
)
print(response.json()["answer"])
```

### JavaScript

```javascript
const API_URL = "https://xxx.execute-api.us-east-1.amazonaws.com/dev";
const headers = { "X-User-Id": "user-123" };

// Upload document
const uploadInfo = await fetch(
  `${API_URL}/upload?filename=doc.pdf&contentType=application/pdf`,
  { headers }
).then(r => r.json());

// Upload to S3
await fetch(uploadInfo.uploadUrl, {
  method: "PUT",
  body: file,
  headers: { "Content-Type": file.type }
});

// Ask question
const answer = await fetch(
  `${API_URL}/documents/${uploadInfo.documentId}/query`,
  {
    method: "POST",
    headers: { ...headers, "Content-Type": "application/json" },
    body: JSON.stringify({ question: "What is this document about?" })
  }
).then(r => r.json());

console.log(answer.answer);
```
