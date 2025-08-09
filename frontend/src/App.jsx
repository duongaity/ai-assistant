import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import ChatAssistant from './components/ChatAssistant';
import CodeEditor from './components/CodeEditor';
import HomePage from './pages/HomePage';
import KnowledgeBasePage from './pages/KnowledgeBasePage';
import './App.css';

const API_BASE_URL = 'http://localhost:8888/api';

function App() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('java');
  const [commentedCode, setCommentedCode] = useState('');
  const [tokensInfo, setTokensInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [supportedLanguages, setSupportedLanguages] = useState([]);
  const fileInputRef = useRef(null);
  const [chatVisible, setChatVisible] = useState(false);
  const [currentPage, setCurrentPage] = useState(() => {
    // Check URL path to determine initial page
    const path = window.location.pathname;
    if (path === '/knowledge-base') {
      return 'knowledge-base';
    }
    return 'home';
  }); // Add page state

  useEffect(() => {
    // Fetch supported languages - Lấy danh sách ngôn ngữ được hỗ trợ
    const fetchLanguages = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/languages`);
        if (response.data.success) {
          setSupportedLanguages(response.data.languages);
        }
      } catch (err) {
        console.error('Error fetching languages:', err);
      }
    };

    fetchLanguages();
  }, []);

  const handleLanguageChange = (newLanguage) => {
    setLanguage(newLanguage);
    setCommentedCode('');
    setTokensInfo(null);
    setError('');
  };

  const handleClearAll = () => {
    setCode('');
    setCommentedCode('');
    setTokensInfo(null);
    setError('');
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Check file size (limit to 5MB) - Kiểm tra kích thước file (giới hạn 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('File is too large. Please select a file smaller than 5MB.');
      return;
    }

    // Check file type - Kiểm tra loại file
    const allowedExtensions = ['.txt', '.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.clj', '.sh', '.sql', '.html', '.css', '.json', '.xml', '.yaml', '.yml'];
    const fileName = file.name.toLowerCase();
    const isAllowed = allowedExtensions.some(ext => fileName.endsWith(ext));
    
    if (!isAllowed) {
      setError('File format not supported. Please select a valid code file.');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target.result;
      setCode(content);
      setCommentedCode('');
      setTokensInfo(null);
      setError('');
      
      // Auto-detect language from file extension - Tự động phát hiện ngôn ngữ từ phần mở rộng file
      const ext = fileName.split('.').pop();
      const languageMap = {
        'js': 'javascript',
        'jsx': 'javascript',
        'ts': 'typescript',
        'tsx': 'typescript',
        'py': 'python',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c',
        'cs': 'csharp',
        'php': 'php',
        'rb': 'ruby',
        'go': 'go',
        'rs': 'rust',
        'swift': 'swift',
        'kt': 'kotlin',
        'scala': 'scala',
        'clj': 'clojure',
        'sh': 'bash',
        'sql': 'sql'
      };
      
      if (languageMap[ext]) {
        setLanguage(languageMap[ext]);
      }
    };
    
    reader.onerror = () => {
      setError('Cannot read file. Please try again.');
    };
    
    reader.readAsText(file);
    
    // Reset input value to allow selecting the same file again - Reset giá trị input để cho phép chọn lại cùng file
    event.target.value = '';
  };

  const triggerFileUpload = () => {
    if (fileInputRef) {
      fileInputRef.click();
    }
  };

  const toggleChat = () => {
    setChatVisible(!chatVisible);
  };

  const handleChatResult = (result, tokensData) => {
    setCommentedCode(result);
    setTokensInfo(tokensData);
    setError('');
  };

  // Quick Action handlers - Xử lý các Quick Action
  const handleQuickAction = async (actionType, prompt) => {
    if (!code.trim()) {
      setError('Please enter code before using Quick Action');
      return;
    }

    setLoading(true);
    setError('');

    const message = `${prompt}\n\n\`\`\`${language}\n${code}\n\`\`\``;

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: message,
        history: [],
        is_quick_action: true
      });

      if (response.data.success) {
        setCommentedCode(response.data.response);
        setTokensInfo(response.data.tokens_info);
        setError('');
      } else {
        setError(response.data.error || 'An error occurred while processing Quick Action');
      }
    } catch (err) {
      console.error('Quick Action error:', err);
      setError('Unable to connect to AI Assistant');
    } finally {
      setLoading(false);
    }
  };

  const handleCommentCode = () => handleQuickAction('comment', 'Add detailed comments in Vietnamese to this code, explain what each part does:');
  const handleFindBugs = () => handleQuickAction('debug', 'Find and fix bugs in this code:');
  const handleOptimize = () => handleQuickAction('optimize', 'Optimize the performance of this code:');
  const handleGenerateTests = () => handleQuickAction('test', 'Generate unit tests for this code:');

  // Navigation handlers
  const navigateToHome = () => {
    setCurrentPage('home');
    window.history.pushState(null, '', '/');
  };
  const navigateToKnowledgeBase = () => {
    setCurrentPage('knowledge-base');
    window.history.pushState(null, '', '/knowledge-base');
  };
  const handleNavigate = (page) => {
    if (page === 'home') {
      navigateToHome();
    } else if (page === 'knowledge-base') {
      navigateToKnowledgeBase();
    }
  };

  // Handle browser back/forward buttons
  useEffect(() => {
    const handlePopState = () => {
      const path = window.location.pathname;
      if (path === '/knowledge-base') {
        setCurrentPage('knowledge-base');
      } else {
        setCurrentPage('home');
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  // Render different pages based on currentPage
  const renderContent = () => {
    if (currentPage === 'knowledge-base') {
      return <KnowledgeBasePage onNavigate={handleNavigate} />;
    }

    // Default home page content
    return (
      <HomePage
        onNavigate={handleNavigate}
        language={language}
        supportedLanguages={supportedLanguages}
        onLanguageChange={handleLanguageChange}
        onFileUpload={handleFileUpload}
        fileInputRef={fileInputRef}
        onClearAll={handleClearAll}
        onCommentCode={handleCommentCode}
        onFindBugs={handleFindBugs}
        onOptimize={handleOptimize}
        onGenerateTests={handleGenerateTests}
        loading={loading}
        code={code}
        setCode={setCode}
        error={error}
        commentedCode={commentedCode}
        tokensInfo={tokensInfo}
      />
    );
  };

  return (
    <div className="App">
      {renderContent()}

      {/* Floating Chat Button - Only show on home page */}
      {currentPage === 'home' && (
        <button
          onClick={toggleChat}
          className={`floating-chat-btn ${chatVisible ? 'active' : ''}`}
          title={chatVisible ? "Close AI Assistant" : "Open AI Assistant"}
        >
          {chatVisible ? '✕' : '🤖'}
        </button>
      )}

      {/* Chat Assistant Sidebar - Only show on home page */}
      {currentPage === 'home' && (
        <ChatAssistant 
          isVisible={chatVisible} 
          onToggle={toggleChat}
          currentCode={code}
          currentLanguage={language}
          onChatResult={handleChatResult}
        />
      )}
    </div>
  );
}

export default App;
