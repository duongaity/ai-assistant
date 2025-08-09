import React, { useState } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import DocumentUpload from '../components/DocumentUpload';
import DocumentList from '../components/DocumentList';
import ChatPanel from '../components/ChatPanel';

// Import highlight.js styles
import 'highlight.js/styles/github.css';

function KnowledgeBasePage({ onNavigate }) {
  const [selectedFiles, setSelectedFiles] = useState([]); // Files được chọn để chat
  const [refreshTrigger, setRefreshTrigger] = useState(0); // Trigger để refresh document list
  
  // Load danh sách files khi component mount
  // (Không cần nữa vì DocumentList sẽ tự load)

  // Handler khi upload thành công
  const handleUploadSuccess = (uploadData) => {
    setRefreshTrigger(prev => prev + 1); // Trigger refresh document list
  };

  // Handler để thêm message từ upload
  const handleUploadMessage = (message) => {
    // This can be handled by the ChatPanel component if needed
    console.log('Upload message:', message);
  };

  // Handler để cập nhật selected files
  const handleFileSelection = (newSelectedFiles) => {
    setSelectedFiles(newSelectedFiles);
  };

  return (
    <div className="d-flex flex-column min-vh-100">
      <Header currentPage="knowledge-base" onNavigate={onNavigate} />
      
      <main className="flex-grow-1 bg-light">
        <div className="container h-100">
          <div className="row h-100 g-3 p-3">
            {/* Left Panel - File Management */}
            <div className="col-lg-4 col-md-5">
              <div className="h-100 d-flex flex-column">
                {/* Document Upload Component */}
                <div className="mb-3">
                  <DocumentUpload 
                    onUploadSuccess={handleUploadSuccess}
                    onMessage={handleUploadMessage}
                  />
                </div>

                {/* Document List Component */}
                <div className="flex-grow-1">
                  <DocumentList 
                    selectedFiles={selectedFiles}
                    onFileSelection={handleFileSelection}
                    refreshTrigger={refreshTrigger}
                  />
                </div>
              </div>
            </div>

            {/* Right Panel - Chat */}
            <div className="col-lg-8 col-md-7">
              <div className="h-100">
                <ChatPanel selectedFiles={selectedFiles} />
              </div>
            </div>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
}

export default KnowledgeBasePage;
