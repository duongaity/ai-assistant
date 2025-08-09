import React, { useState } from 'react';
import axios from 'axios';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './KnowledgeBasePage.css';

const API_BASE_URL = 'http://localhost:8888/api';

function KnowledgeBasePage({ onNavigate }) {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]); // Danh sách files đã upload
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: 'Xin chào! Tôi có thể giúp bạn trả lời các câu hỏi về tài liệu đã upload. Vui lòng upload file (PDF, Word, hoặc Markdown) để bắt đầu.'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [availableFiles, setAvailableFiles] = useState([]); // Danh sách files có sẵn
  const [selectedFiles, setSelectedFiles] = useState([]); // Files được chọn để chat

  // Load danh sách files khi component mount
  React.useEffect(() => {
    loadAvailableFiles();
  }, []);

  const loadAvailableFiles = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/knowledge-base/files`);
      if (response.data.success) {
        setAvailableFiles(response.data.files);
      }
    } catch (error) {
      console.error('Error loading files:', error);
    }
  };

  const handleFileUpload = async (event) => {
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
        setUploading(true);

        try {
          // Upload file to backend
          const formData = new FormData();
          formData.append('file', file);
          formData.append('title', file.name);
          formData.append('description', `Uploaded on ${new Date().toLocaleString()}`);

          const response = await axios.post(`${API_BASE_URL}/knowledge-base/upload`, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });

          if (response.data.success) {
            const newMessage = {
              id: Date.now(),
              type: 'bot',
              content: `Tuyệt vời! Tôi đã nhận được file "${file.name}" với ID: ${response.data.file_id}. Bạn có thể hỏi tôi về nội dung của file này.`
            };
            setMessages(prev => [...prev, newMessage]);
            
            // Reload available files
            loadAvailableFiles();
          } else {
            alert('Lỗi upload: ' + response.data.error);
          }
        } catch (error) {
          console.error('Upload error:', error);
          alert('Lỗi khi upload file: ' + (error.response?.data?.error || error.message));
        } finally {
          setUploading(false);
        }
      } else {
        alert('Vui lòng upload file PDF, Word, hoặc Markdown.');
      }
    }
  };

  const handleFileSelection = (fileId) => {
    setSelectedFiles(prev => {
      if (prev.includes(fileId)) {
        return prev.filter(id => id !== fileId);
      } else {
        return [...prev, fileId];
      }
    });
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage
    };
    
    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputMessage;
    setInputMessage('');
    setIsLoading(true);
    
    try {
      // Prepare chat request
      const chatData = {
        question: currentInput,
        history: messages.map(msg => ({
          type: msg.type,
          content: msg.content
        }))
      };

      // Add selected files if any
      if (selectedFiles.length > 0) {
        chatData.file_ids = selectedFiles;
      }

      const response = await axios.post(`${API_BASE_URL}/knowledge-base/chat`, chatData);

      if (response.data.success) {
        const botMessage = {
          id: Date.now() + 1,
          type: 'bot',
          content: response.data.answer,
          sources: response.data.sources || []
        };
        setMessages(prev => [...prev, botMessage]);
      } else {
        const errorMessage = {
          id: Date.now() + 1,
          type: 'bot',
          content: `Lỗi: ${response.data.error}`
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: `Lỗi kết nối: ${error.response?.data?.error || error.message}`
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
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
          {/* File Upload Section */}
          <div className="file-upload-section">
            <div className="file-upload-container">
              <div className="file-selection">
                <input
                  type="file"
                  id="file-upload"
                  accept=".pdf,.doc,.docx,.md,.txt"
                  onChange={handleFileUpload}
                  style={{ display: 'none' }}
                />
                <label htmlFor="file-upload" className="choose-file-button">
                  Input
                </label>
                <div className="file-display">
                  {uploadedFile ? uploadedFile.name : 'No file selected'}
                </div>
                <button className="upload-button" disabled={!uploadedFile}>
                  Upload File
                </button>
              </div>
            </div>
          </div>

          {/* Chat Section */}
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
