import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  FileText, 
  Loader2, 
  Sparkles, 
  MessageCircle,
  Download,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import ChatInterface from '../components/ChatInterface';
import { Document, QueryResponse } from '../types';
import { documentService } from '../services/api';

interface ChatMessage {
  type: 'question' | 'answer';
  content: string;
  confidence?: string;
  timestamp: Date;
}

export default function DocumentPage() {
  const { documentId } = useParams<{ documentId: string }>();
  const [document, setDocument] = useState<Document | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isExtracting, setIsExtracting] = useState(false);
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [summary, setSummary] = useState<string | null>(null);
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (documentId) {
      fetchDocument();
    }
  }, [documentId]);

  const fetchDocument = async () => {
    try {
      setIsLoading(true);
      const { document: doc } = await documentService.getDocument(
        documentId!,
        true,
        true
      );
      setDocument(doc);
      
      // Load existing summary if available
      if (doc.summary) {
        setSummary(doc.summary);
      }
      
      // Load chat history
      if (doc.queryHistory) {
        const messages: ChatMessage[] = [];
        doc.queryHistory.forEach(item => {
          messages.push({
            type: 'question',
            content: item.question,
            timestamp: new Date(item.timestamp)
          });
          messages.push({
            type: 'answer',
            content: item.answer,
            timestamp: new Date(item.timestamp)
          });
        });
        setChatMessages(messages);
      }
    } catch (err) {
      setError('Failed to load document');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExtract = async () => {
    if (!documentId) return;
    
    try {
      setIsExtracting(true);
      const result = await documentService.extractText(documentId);
      setDocument(prev => prev ? {
        ...prev,
        extractedText: result.text,
        wordCount: result.wordCount,
        status: 'EXTRACTED'
      } : null);
    } catch (err) {
      setError('Failed to extract text');
      console.error(err);
    } finally {
      setIsExtracting(false);
    }
  };

  const handleSummarize = async () => {
    if (!documentId) return;
    
    try {
      setIsSummarizing(true);
      const result = await documentService.summarize(documentId, {
        questions: true,
        maxLength: 500
      });
      setSummary(result.summary);
      if (result.suggestedQuestions) {
        setSuggestedQuestions(result.suggestedQuestions);
      }
    } catch (err) {
      setError('Failed to generate summary');
      console.error(err);
    } finally {
      setIsSummarizing(false);
    }
  };

  const handleAskQuestion = async (question: string) => {
    if (!documentId) return;
    
    // Add question to chat
    setChatMessages(prev => [...prev, {
      type: 'question',
      content: question,
      timestamp: new Date()
    }]);

    try {
      const result = await documentService.askQuestion(documentId, question);
      
      // Add answer to chat
      setChatMessages(prev => [...prev, {
        type: 'answer',
        content: result.answer,
        confidence: result.confidence,
        timestamp: new Date()
      }]);
    } catch (err) {
      setChatMessages(prev => [...prev, {
        type: 'answer',
        content: 'Sorry, I encountered an error processing your question.',
        timestamp: new Date()
      }]);
    }
  };

  const getStatusIcon = (status: Document['status']) => {
    switch (status) {
      case 'COMPLETED':
      case 'EXTRACTED':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'PROCESSING':
        return <Loader2 className="w-5 h-5 text-yellow-500 animate-spin" />;
      case 'FAILED':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          {error || 'Document not found'}
        </h2>
        <Link
          to="/documents"
          className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to documents
        </Link>
      </div>
    );
  }

  const canInteract = document.status === 'EXTRACTED' || document.status === 'COMPLETED';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back Link */}
      <Link
        to="/documents"
        className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to documents
      </Link>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left Column - Document Info */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl border border-gray-200 p-6 sticky top-24">
            {/* Document Header */}
            <div className="flex items-start gap-4 mb-6">
              <div className="p-3 bg-primary-50 rounded-lg">
                <FileText className="w-8 h-8 text-primary-500" />
              </div>
              <div className="flex-1 min-w-0">
                <h1 className="font-semibold text-gray-900 truncate">
                  {document.filename}
                </h1>
                <div className="flex items-center gap-2 mt-1">
                  {getStatusIcon(document.status)}
                  <span className="text-sm text-gray-500">{document.status}</span>
                </div>
              </div>
            </div>

            {/* Metadata */}
            <div className="space-y-3 text-sm">
              {document.wordCount && (
                <div className="flex justify-between">
                  <span className="text-gray-500">Words</span>
                  <span className="font-medium">{document.wordCount.toLocaleString()}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-gray-500">Uploaded</span>
                <span className="font-medium">
                  {new Date(document.createdAt).toLocaleDateString()}
                </span>
              </div>
            </div>

            {/* Actions */}
            <div className="mt-6 space-y-3">
              {document.status === 'UPLOADED' && (
                <button
                  onClick={handleExtract}
                  disabled={isExtracting}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50"
                >
                  {isExtracting ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <FileText className="w-4 h-4" />
                  )}
                  Extract Text
                </button>
              )}

              {canInteract && !summary && (
                <button
                  onClick={handleSummarize}
                  disabled={isSummarizing}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50"
                >
                  {isSummarizing ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Sparkles className="w-4 h-4" />
                  )}
                  Generate Summary
                </button>
              )}

              {document.downloadUrl && (
                <a
                  href={document.downloadUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200"
                >
                  <Download className="w-4 h-4" />
                  Download Original
                </a>
              )}
            </div>
          </div>
        </div>

        {/* Right Column - Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Summary Section */}
          {(summary || isSummarizing) && (
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-4">
                <Sparkles className="w-5 h-5 text-purple-500" />
                AI Summary
              </h2>
              {isSummarizing ? (
                <div className="flex items-center gap-3 text-gray-500">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Generating summary...
                </div>
              ) : (
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown>{summary || ''}</ReactMarkdown>
                </div>
              )}

              {/* Suggested Questions */}
              {suggestedQuestions.length > 0 && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <h3 className="text-sm font-medium text-gray-700 mb-3">
                    Suggested Questions
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {suggestedQuestions.map((question, index) => (
                      <button
                        key={index}
                        onClick={() => handleAskQuestion(question)}
                        className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition-colors"
                      >
                        {question}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Q&A Section */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-4">
              <MessageCircle className="w-5 h-5 text-primary-500" />
              Ask Questions
            </h2>

            {!canInteract ? (
              <div className="text-center py-8 text-gray-500">
                <p>Extract text from the document first to enable Q&A.</p>
              </div>
            ) : (
              <>
                {/* Chat Messages */}
                {chatMessages.length > 0 && (
                  <div className="mb-6 space-y-4 max-h-96 overflow-y-auto">
                    {chatMessages.map((msg, index) => (
                      <div
                        key={index}
                        className={`flex ${msg.type === 'question' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[80%] px-4 py-3 rounded-xl ${
                            msg.type === 'question'
                              ? 'bg-primary-600 text-white'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          <p className="text-sm">{msg.content}</p>
                          {msg.confidence && (
                            <p className={`text-xs mt-1 ${
                              msg.type === 'question' ? 'text-primary-200' : 'text-gray-500'
                            }`}>
                              Confidence: {msg.confidence}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Chat Input */}
                <ChatInterface
                  onSendMessage={handleAskQuestion}
                  disabled={!canInteract}
                  placeholder="Ask a question about this document..."
                />
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
