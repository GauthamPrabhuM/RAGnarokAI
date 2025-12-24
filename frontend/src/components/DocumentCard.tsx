import { Link } from 'react-router-dom';
import { FileText, Clock, Trash2, Eye, Loader2 } from 'lucide-react';
import { Document } from '../types';

interface DocumentCardProps {
  document: Document;
  onDelete?: (id: string) => void;
  isDeleting?: boolean;
}

export default function DocumentCard({ document, onDelete, isDeleting }: DocumentCardProps) {
  const getStatusBadge = (status: Document['status']) => {
    const styles = {
      UPLOADED: 'bg-blue-100 text-blue-700',
      PROCESSING: 'bg-yellow-100 text-yellow-700',
      EXTRACTED: 'bg-purple-100 text-purple-700',
      COMPLETED: 'bg-green-100 text-green-700',
      FAILED: 'bg-red-100 text-red-700',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {status}
      </span>
    );
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getFileIcon = () => {
    // Could add different icons based on content type
    return <FileText className="w-10 h-10 text-primary-500" />;
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-4">
        {/* File Icon */}
        <div className="p-3 bg-primary-50 rounded-lg">
          {getFileIcon()}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <h3 className="font-medium text-gray-900 truncate">
                {document.filename}
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                {formatFileSize(document.fileSize)}
              </p>
            </div>
            {getStatusBadge(document.status)}
          </div>

          {/* Summary preview if available */}
          {document.summary && (
            <p className="text-sm text-gray-600 mt-2 line-clamp-2">
              {document.summary}
            </p>
          )}

          {/* Metadata */}
          <div className="flex items-center gap-4 mt-3 text-xs text-gray-400">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {formatDate(document.createdAt)}
            </span>
            {document.wordCount && (
              <span>{document.wordCount.toLocaleString()} words</span>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 mt-4">
            <Link
              to={`/documents/${document.documentId}`}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-primary-50 text-primary-700 rounded-lg text-sm font-medium hover:bg-primary-100 transition-colors"
            >
              <Eye className="w-4 h-4" />
              View
            </Link>
            {onDelete && (
              <button
                onClick={() => onDelete(document.documentId)}
                disabled={isDeleting}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-red-50 text-red-700 rounded-lg text-sm font-medium hover:bg-red-100 transition-colors disabled:opacity-50"
              >
                {isDeleting ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Trash2 className="w-4 h-4" />
                )}
                Delete
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
