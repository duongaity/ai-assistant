import React, { useState } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './KnowledgeBasePage.css';

function KnowledgeBasePage({ onNavigate }) {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: 'Hello! I can help you with questions about your uploaded documents. Please upload a file (PDF, Word, or Markdown) to get started.'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const allowedTypes = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/markdown',
        'text/plain'
      ];
      
      if (allowedTypes.includes(file.type) || file.name.endsWith('.md')) {
        setUploadedFile(file);
        const newMessage = {
          id: Date.now(),
          type: 'bot',
          content: `Great! I've received your file "${file.name}". You can now ask me questions about its content.`
        };
        setMessages(prev => [...prev, newMessage]);
      } else {
        alert('Please upload a PDF, Word document, or Markdown file.');
      }
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    
    // Simulate AI response
    setTimeout(() => {
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: `I understand your question about "${inputMessage}". ${uploadedFile ? `Based on your uploaded file "${uploadedFile.name}", ` : ''}I'll help you find the relevant information. (This is a demo response - integrate with your AI service for actual functionality.)`
      };
      setMessages(prev => [...prev, botMessage]);
      setIsLoading(false);
    }, 1000);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="page-container">
      <Header currentPage="knowledge-base" onNavigate={onNavigate} />
      
      <main className="knowledge-base-main">
        <div className="knowledge-base-container">
          {/* Chat Section with integrated file upload */}
          <div className="chat-section">
            <div className="chat-container">
              <div className="chat-messages">
                {messages.map((message) => (
                  <div key={message.id} className={`message ${message.type}`}>
                    <div className="message-content">
                      {message.content}
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="message bot">
                    <div className="message-content">
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="chat-input">
                <div className="input-container">
                  <input
                    type="file"
                    id="file-upload"
                    accept=".pdf,.doc,.docx,.md,.txt"
                    onChange={handleFileUpload}
                    style={{ display: 'none' }}
                  />
                  <label htmlFor="file-upload" className="file-upload-btn">
                    <span>📎</span>
                  </label>
                  
                  {uploadedFile && (
                    <div className="uploaded-file-indicator">
                      <span className="file-name">{uploadedFile.name}</span>
                    </div>
                  )}
                  
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask a question about your uploaded document..."
                    rows="2"
                    disabled={isLoading}
                  />
                  <button 
                    onClick={handleSendMessage} 
                    disabled={!inputMessage.trim() || isLoading}
                    className="send-button"
                  >
                    <span>📤</span>
                  </button>
                </div>
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
