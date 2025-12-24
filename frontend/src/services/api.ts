import axios from 'axios';
import { Document, UploadResponse, ExtractResponse, SummaryResponse, QueryResponse } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add user ID header to all requests
api.interceptors.request.use((config) => {
  const userId = localStorage.getItem('userId') || 'demo-user';
  config.headers['X-User-Id'] = userId;
  return config;
});

export const documentService = {
  // Get presigned URL for upload
  async getUploadUrl(filename: string, contentType: string): Promise<UploadResponse> {
    const response = await api.get('/upload', {
      params: { filename, contentType },
    });
    return response.data;
  },

  // Upload file to S3 using presigned URL
  async uploadToS3(uploadUrl: string, file: File): Promise<void> {
    await axios.put(uploadUrl, file, {
      headers: {
        'Content-Type': file.type,
      },
    });
  },

  // Confirm upload and create document record
  async confirmUpload(
    documentId: string,
    s3Key: string,
    filename: string,
    contentType: string,
    fileSize: number
  ): Promise<{ document: Document }> {
    const response = await api.post('/upload', {
      documentId,
      s3Key,
      filename,
      contentType,
      fileSize,
    });
    return response.data;
  },

  // Full upload flow
  async uploadDocument(file: File): Promise<Document> {
    // Step 1: Get presigned URL
    const { uploadUrl, documentId, s3Key } = await this.getUploadUrl(
      file.name,
      file.type
    );

    // Step 2: Upload to S3
    await this.uploadToS3(uploadUrl, file);

    // Step 3: Confirm upload
    const { document } = await this.confirmUpload(
      documentId,
      s3Key,
      file.name,
      file.type,
      file.size
    );

    return document;
  },

  // List all documents
  async listDocuments(limit = 50): Promise<{ documents: Document[]; count: number }> {
    const response = await api.get('/documents', {
      params: { limit },
    });
    return response.data;
  },

  // Get single document
  async getDocument(
    documentId: string,
    includeText = false,
    includeHistory = false
  ): Promise<{ document: Document }> {
    const response = await api.get(`/documents/${documentId}`, {
      params: { includeText, includeHistory },
    });
    return response.data;
  },

  // Delete document
  async deleteDocument(documentId: string): Promise<void> {
    await api.delete(`/documents/${documentId}`);
  },

  // Extract text from document
  async extractText(documentId: string): Promise<ExtractResponse> {
    const response = await api.post(`/documents/${documentId}/extract`);
    return response.data;
  },

  // Get document summary
  async summarize(
    documentId: string,
    options?: { entities?: boolean; questions?: boolean; maxLength?: number }
  ): Promise<SummaryResponse> {
    const response = await api.get(`/documents/${documentId}/summarize`, {
      params: options,
    });
    return response.data;
  },

  // Ask question about document
  async askQuestion(documentId: string, question: string): Promise<QueryResponse> {
    const response = await api.post(`/documents/${documentId}/query`, {
      question,
    });
    return response.data;
  },
};

export default api;
