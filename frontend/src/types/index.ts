export interface Document {
  documentId: string;
  userId: string;
  filename: string;
  s3Key: string;
  contentType: string;
  fileSize: number;
  status: 'UPLOADED' | 'PROCESSING' | 'EXTRACTED' | 'COMPLETED' | 'FAILED';
  createdAt: string;
  updatedAt: string;
  summary?: string;
  extractedText?: string;
  wordCount?: number;
  ocrConfidence?: string;
  downloadUrl?: string;
  queryHistory?: QueryHistoryItem[];
}

export interface QueryHistoryItem {
  question: string;
  answer: string;
  timestamp: string;
}

export interface UploadResponse {
  uploadUrl: string;
  documentId: string;
  s3Key: string;
  expiresIn: number;
}

export interface ExtractResponse {
  documentId: string;
  text: string;
  wordCount: number;
  confidence: number;
  cached: boolean;
}

export interface SummaryResponse {
  documentId: string;
  summary: string;
  wordCount: number;
  cached: boolean;
  entities?: Record<string, string[]>;
  suggestedQuestions?: string[];
}

export interface QueryResponse {
  documentId: string;
  question: string;
  answer: string;
  confidence: 'high' | 'medium' | 'low';
}
