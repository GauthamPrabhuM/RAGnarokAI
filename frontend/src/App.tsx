import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useState } from 'react';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import DocumentPage from './pages/DocumentPage';
import DocumentsPage from './pages/DocumentsPage';
import { Document } from './types';

function App() {
  const [documents, setDocuments] = useState<Document[]>([]);

  const addDocument = (doc: Document) => {
    setDocuments(prev => [doc, ...prev]);
  };

  const removeDocument = (id: string) => {
    setDocuments(prev => prev.filter(d => d.documentId !== id));
  };

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route 
            path="/" 
            element={<HomePage onUpload={addDocument} />} 
          />
          <Route 
            path="/documents" 
            element={
              <DocumentsPage 
                documents={documents} 
                setDocuments={setDocuments}
                onDelete={removeDocument} 
              />
            } 
          />
          <Route 
            path="/documents/:documentId" 
            element={<DocumentPage />} 
          />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
