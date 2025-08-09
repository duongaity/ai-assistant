import React, { useState, useRef } from 'react';
import axios from 'axios';
import MessageContent from './MessageContent';
import './ChatPanel.css';

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

function ChatPanel({ selectedFiles = [] }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: 'Hello! I\'m your AI assistant. Upload documents and ask me anything about them.'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // State + ref để điều khiển audio TTS
  const [audioPlayingIndex, setAudioPlayingIndex] = useState(null);
  const audioRef = useRef(null);

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
    <div className="chat-panel">
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
      
      {/* Thẻ audio ẩn dùng để phát TTS */}
      <audio
        ref={audioRef}
        onEnded={handleAudioEnded}
        style={{ display: 'none' }}
      />
    </div>
  );
}

export default ChatPanel;
