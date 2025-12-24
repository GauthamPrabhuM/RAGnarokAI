import { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Brain, FileText, Home, Github } from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2">
              <Brain className="w-8 h-8 text-primary-600" />
              <span className="text-xl font-bold text-gray-900">
                RAGnarok<span className="text-primary-600">AI</span>
              </span>
            </Link>

            {/* Navigation */}
            <nav className="flex items-center gap-6">
              <Link
                to="/"
                className={`flex items-center gap-1.5 text-sm font-medium transition-colors ${
                  isActive('/') 
                    ? 'text-primary-600' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Home className="w-4 h-4" />
                Home
              </Link>
              <Link
                to="/documents"
                className={`flex items-center gap-1.5 text-sm font-medium transition-colors ${
                  isActive('/documents') 
                    ? 'text-primary-600' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <FileText className="w-4 h-4" />
                Documents
              </Link>
              <a
                href="https://github.com/GauthamPrabhuM/RAGnarokAI"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
              >
                <Github className="w-4 h-4" />
                GitHub
              </a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-500">
              © 2024 RAGnarokAI. Built with AWS & React.
            </p>
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span>Powered by</span>
              <span className="font-medium text-gray-700">Amazon Bedrock</span>
              <span>•</span>
              <span className="font-medium text-gray-700">Amazon Textract</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
