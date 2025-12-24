import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Loader2, CheckCircle, XCircle } from 'lucide-react';
import { documentService } from '../services/api';
import { Document } from '../types';

interface FileUploadProps {
  onUploadComplete: (document: Document) => void;
}

type UploadStatus = 'idle' | 'uploading' | 'success' | 'error';

export default function FileUpload({ onUploadComplete }: FileUploadProps) {
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [currentFile, setCurrentFile] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setCurrentFile(file.name);
    setUploadStatus('uploading');
    setUploadProgress(0);
    setError(null);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const document = await documentService.uploadDocument(file);

      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadStatus('success');
      onUploadComplete(document);

      // Reset after delay
      setTimeout(() => {
        setUploadStatus('idle');
        setCurrentFile(null);
        setUploadProgress(0);
      }, 2000);

    } catch (err) {
      setUploadStatus('error');
      setError(err instanceof Error ? err.message : 'Upload failed');
    }
  }, [onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'text/plain': ['.txt'],
    },
    maxSize: 10 * 1024 * 1024, // 10 MB
    multiple: false,
  });

  return (
    <div
      {...getRootProps()}
      className={`
        relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
        transition-all duration-200
        ${isDragActive 
          ? 'border-primary-500 bg-primary-50' 
          : 'border-gray-300 hover:border-gray-400 bg-white'
        }
        ${uploadStatus === 'uploading' ? 'pointer-events-none' : ''}
      `}
    >
      <input {...getInputProps()} />

      {uploadStatus === 'idle' && (
        <>
          <Upload className={`w-12 h-12 mx-auto mb-4 ${
            isDragActive ? 'text-primary-500' : 'text-gray-400'
          }`} />
          <p className="text-lg font-medium text-gray-700 mb-2">
            {isDragActive 
              ? 'Drop your document here' 
              : 'Drag & drop your document here'
            }
          </p>
          <p className="text-sm text-gray-500 mb-4">
            or click to browse
          </p>
          <div className="flex justify-center gap-2 flex-wrap">
            {['PDF', 'PNG', 'JPEG', 'TXT'].map(format => (
              <span
                key={format}
                className="px-2 py-1 bg-gray-100 rounded text-xs font-medium text-gray-600"
              >
                {format}
              </span>
            ))}
          </div>
          <p className="text-xs text-gray-400 mt-2">Max file size: 10 MB</p>
        </>
      )}

      {uploadStatus === 'uploading' && (
        <div className="py-4">
          <Loader2 className="w-12 h-12 mx-auto mb-4 text-primary-500 animate-spin" />
          <p className="text-lg font-medium text-gray-700 mb-2">
            Uploading {currentFile}...
          </p>
          <div className="w-full max-w-xs mx-auto bg-gray-200 rounded-full h-2 mt-4">
            <div
              className="bg-primary-500 h-2 rounded-full transition-all duration-200"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
          <p className="text-sm text-gray-500 mt-2">{uploadProgress}%</p>
        </div>
      )}

      {uploadStatus === 'success' && (
        <div className="py-4">
          <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-500" />
          <p className="text-lg font-medium text-gray-700">
            Upload complete!
          </p>
          <p className="text-sm text-gray-500 mt-1">
            {currentFile}
          </p>
        </div>
      )}

      {uploadStatus === 'error' && (
        <div className="py-4">
          <XCircle className="w-12 h-12 mx-auto mb-4 text-red-500" />
          <p className="text-lg font-medium text-gray-700 mb-2">
            Upload failed
          </p>
          <p className="text-sm text-red-500">{error}</p>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setUploadStatus('idle');
              setError(null);
            }}
            className="mt-4 px-4 py-2 bg-gray-100 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-200"
          >
            Try again
          </button>
        </div>
      )}
    </div>
  );
}
