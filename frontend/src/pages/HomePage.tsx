import { useNavigate } from 'react-router-dom';
import { Sparkles, FileSearch, MessageCircle, Zap } from 'lucide-react';
import FileUpload from '../components/FileUpload';
import { Document } from '../types';

interface HomePageProps {
  onUpload: (doc: Document) => void;
}

export default function HomePage({ onUpload }: HomePageProps) {
  const navigate = useNavigate();

  const handleUploadComplete = (document: Document) => {
    onUpload(document);
    // Navigate to the document page
    navigate(`/documents/${document.documentId}`);
  };

  const features = [
    {
      icon: FileSearch,
      title: 'Smart Text Extraction',
      description: 'Powered by Amazon Textract, extract text from PDFs, images, and documents with high accuracy OCR.',
    },
    {
      icon: Sparkles,
      title: 'AI Summarization',
      description: 'Get instant, intelligent summaries of your documents using Claude 3 via Amazon Bedrock.',
    },
    {
      icon: MessageCircle,
      title: 'Document Q&A',
      description: 'Ask questions about your documents and get accurate answers with context.',
    },
    {
      icon: Zap,
      title: 'Serverless & Fast',
      description: 'Built on AWS Lambda for instant scaling and pay-per-use pricing.',
    },
  ];

  return (
    <div className="min-h-[calc(100vh-8rem)]">
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-primary-50 to-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
              Unleash the Power of{' '}
              <span className="text-primary-600">AI</span> on Your Documents
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Upload any document and instantly extract text, generate summaries, 
              and ask questions using RAG-powered intelligence on AWS.
            </p>
          </div>

          {/* Upload Section */}
          <div className="max-w-xl mx-auto mt-8">
            <FileUpload onUploadComplete={handleUploadComplete} />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-12">
            Powered by AWS AI Services
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-white rounded-xl p-6 border border-gray-200 hover:shadow-lg transition-shadow"
              >
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* AWS Services Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Built With
          </h2>
          <div className="flex flex-wrap justify-center gap-6">
            {[
              'Amazon Bedrock',
              'Amazon Textract',
              'AWS Lambda',
              'Amazon S3',
              'Amazon DynamoDB',
              'API Gateway',
              'AWS SAM',
            ].map((service) => (
              <span
                key={service}
                className="px-4 py-2 bg-white rounded-full border border-gray-200 text-sm font-medium text-gray-700"
              >
                {service}
              </span>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
