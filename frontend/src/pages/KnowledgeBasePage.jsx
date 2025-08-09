import React, { useState, useRef } from 'react';
import axios from 'axios';
import Header from '../components/Header';
import Footer from '../components/Footer';
import MessageContent from '../components/MessageContent';
import './KnowledgeBasePage.css';

// Import highlight.js styles
import 'highlight.js/styles/github.css';

const API_BASE_URL = 'http://localhost:8888/api';

// Helper function to convert base64 string to Blob
function base64ToBlob(base64, mime) {
  const byteChars = atob(base64);
  const byteNumbers = new Array(byteChars.length);
  for (let i = 0; i < byteChars.length; i++) {
    byteNumbers[i] = byteChars.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  return new Blob([byteArray], { type: mime });
}

function KnowledgeBasePage({ onNavigate }) {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: 'Hello! I\'m your AI assistant. Upload documents and ask me anything about them.'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [availableFiles, setAvailableFiles] = useState([]); // Danh sách files có sẵn
  const [selectedFiles, setSelectedFiles] = useState([]); // Files được chọn để chat

    // State + ref để điều khiển audio TTS
  const [audioPlayingIndex, setAudioPlayingIndex] = useState(null);
  const audioRef = useRef(null);
  
  // Load danh sách files khi component mount
  React.useEffect(() => {
    loadAvailableFiles();
  }, []);

    // Hàm play/pause TTS cho message index
  const handlePlayTTS = async (text, index) => {
    if (audioPlayingIndex === index) {
      // Đang phát, bấm lại để dừng
      if (audioRef.current) {
        audioRef.current.pause();
      }
      setAudioPlayingIndex(null);
      return;
    }

    try {
      console.log('Starting TTS for text:', text.substring(0, 50) + '...');
      
      const response = await axios.post('http://localhost:8888/api/tts', {
        text: text
      });

      console.log('TTS API response:', response.data);

      if (response.data.success) {
        const audioBase64 = response.data.audio_base64;
        const mimeType = response.data.mimeType || 'audio/wav';
        console.log('Audio base64 length:', audioBase64.length);
        console.log('Audio MIME type:', mimeType);
        
        const audioBlob = base64ToBlob(audioBase64, mimeType);
        console.log('Audio blob size:', audioBlob.size, 'type:', audioBlob.type);
        
        const audioUrl = URL.createObjectURL(audioBlob);
        console.log('Audio URL created:', audioUrl);
        
        if (audioRef.current) {
          // Clean up previous audio
          if (audioRef.current.src) {
            URL.revokeObjectURL(audioRef.current.src);
          }
          
          audioRef.current.src = audioUrl;
          audioRef.current.onloadeddata = () => {
            console.log('Audio loaded successfully, duration:', audioRef.current.duration);
          };
          audioRef.current.onerror = (e) => {
            console.error('Audio load error:', e);
            console.error('Audio error details:', audioRef.current.error);
          };
          
          try {
            await audioRef.current.play();
            setAudioPlayingIndex(index);
            console.log('Audio playing started');
          } catch (playError) {
            console.error('Audio play error:', playError);
            
            // Try alternative approach with HTML5 Audio API
            try {
              const audio = new Audio();
              audio.src = audioUrl;
              await audio.play();
              setAudioPlayingIndex(index);
              console.log('Alternative audio playing started');
            } catch (altError) {
              console.error('Alternative audio play error:', altError);
            }
          }
        }
      } else {
        console.error('TTS API failed:', response.data.error);
      }
    } catch (error) {
      console.error('Error calling TTS API:', error);
    }
  };

  const handleAudioEnded = () => {
    setAudioPlayingIndex(null);
  };

  const loadAvailableFiles = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/knowledge-base/files`);
      if (response.data.success && response.data.data && response.data.data.files) {
        setAvailableFiles(response.data.data.files);
      } else {
        setAvailableFiles([]);
      }
    } catch (error) {
      console.error('Error loading files:', error);
      setAvailableFiles([]);
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
      } else {
        alert('Please select PDF, Word, or Markdown files.');
        event.target.value = ''; // Reset input
      }
    }
  };

  const handleUploadClick = async () => {
    if (!uploadedFile) return;

    setUploading(true);
    try {
      // Upload file to backend
      const formData = new FormData();
      formData.append('file', uploadedFile);
      formData.append('title', uploadedFile.name);
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
          content: `Great! I've received the file "${uploadedFile.name}" with ID: ${response.data.file_id}. You can now ask me about the content of this file.`
        };
        setMessages(prev => [...prev, newMessage]);
        
        // Reset uploaded file và reload available files
        setUploadedFile(null);
        document.getElementById('file-upload').value = '';
        loadAvailableFiles();
      } else {
        alert('Upload error: ' + response.data.error);
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('File upload error: ' + (error.response?.data?.error || error.message));
    } finally {
      setUploading(false);
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
        message: currentInput,
        max_results: 50
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
          content: response.data.response,
          sources: response.data.sources || []
        };
        setMessages(prev => [...prev, botMessage]);
      } else {
        const errorMessage = {
          id: Date.now() + 1,
          type: 'bot',
          content: `Error: ${response.data.error}`
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: `Connection error: ${error.response?.data?.error || error.message}`
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
          {/* Left Panel - File Management */}
          <div className="left-panel">
            {/* File Upload Section */}
            <div className="file-upload-section">
              <h3>📁 Upload Documents</h3>
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
                    {uploading ? 'Uploading...' : 'Choose File'}
                  </label>
                  <div className="file-display">
                    {uploadedFile ? uploadedFile.name : 'No file selected'}
                  </div>
                  {uploadedFile && (
                    <button 
                      className="upload-button" 
                      onClick={handleUploadClick}
                      disabled={uploading}
                    >
                      {uploading ? 'Uploading...' : 'Upload'}
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* File List Section */}
            <div className="file-list-section">
              <h3>📚 Document List ({availableFiles?.length || 0})</h3>
              {availableFiles && availableFiles.length > 0 ? (
                <div className="file-list">
                  <div className="select-all-controls">
                    <button 
                      className="select-button"
                      onClick={() => setSelectedFiles(availableFiles?.map(file => file.file_id) || [])}
                    >
                      Select All
                    </button>
                    <button 
                      className="select-button"
                      onClick={() => setSelectedFiles([])}
                    >
                      Deselect All
                    </button>
                  </div>
                  
                  <div className="files-list">
                    {availableFiles && availableFiles.map((file) => (
                      <div 
                        key={file.file_id} 
                        className={`file-item ${selectedFiles.includes(file.file_id) ? 'selected' : ''}`}
                        onClick={() => handleFileSelection(file.file_id)}
                      >
                        <div className="file-checkbox">
                          <input
                            type="checkbox"
                            checked={selectedFiles.includes(file.file_id)}
                            onChange={() => handleFileSelection(file.file_id)}
                            onClick={(e) => e.stopPropagation()}
                          />
                          <span className="checkmark"></span>
                        </div>
                        <div className="file-info">
                          <div className="file-title">{file.filename}</div>
                          <div className="file-uuid">ID: {file.file_id}</div>
                          <div className="file-upload-time">
                            📅 {new Date(file.upload_time).toLocaleString('en-US')}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="no-files">
                  <p>No documents yet. Upload files to get started!</p>
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - Chat */}
          <div className="right-panel">
            <div className="chat-section">
              <div className="chat-header">
                <h3>💬 AI Assistant</h3>
                <div className="chat-info">
                  {selectedFiles.length > 0 ? (
                    <span>Chatting with {selectedFiles.length} selected document(s)</span>
                  ) : (
                    <span>Chatting with all documents</span>
                  )}
                </div>
              </div>
              
              <div className="chat-container">
                <div className="chat-messages">
                  {messages.map((message, index) => (
                    <div key={message.id} className={`message ${message.type}`}>
                      <div className="message-content">
                        <MessageContent content={message.content} type={message.type} />
                        {message.type === 'bot' && (
                          <div className="message-actions">
                            <button
                              className="tts-btn"
                              onClick={() => handlePlayTTS(message.content, index)}
                              title="Play audio"
                            >
                              {audioPlayingIndex === index ? '⏸️' : '🔊'}
                            </button>
                          </div>
                        )}
                        {message.sources && message.sources.length > 0 && (
                          <div className="message-sources">
                            <details>
                              <summary>📖 Nguồn tham khảo ({message.sources.length})</summary>
                              <div className="sources-list">
                                {message.sources.map((source, index) => (
                                  <div key={index} className="source-item">
                                    <div className="source-title">{source.source.title}</div>
                                    <div className="source-content">{source.content.substring(0, 200)}...</div>
                                    <div className="source-score">Độ liên quan: {(source.similarity_score * 100).toFixed(1)}%</div>
                                  </div>
                                ))}
                              </div>
                            </details>
                          </div>
                        )}
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
                      placeholder="Ask about your documents..."
                      rows="3"
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
        </div>
      </main>
      
      <Footer />
      
      {/* Thẻ audio ẩn dùng để phát TTS */}
      <audio
        ref={audioRef}
        onEnded={handleAudioEnded}
        style={{ display: 'none' }}
      />
    </div>
  );
}

export default KnowledgeBasePage;
