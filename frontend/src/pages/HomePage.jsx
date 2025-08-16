import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import Header from '../components/Header';
import Footer from '../components/Footer';
import HowToUse from '../components/HowToUse';
import CodeEditor from '../components/CodeEditor';

function HomePage({
  onNavigate,
  language,
  supportedLanguages,
  onLanguageChange,
  onFileUpload,
  fileInputRef,
  onClearAll,
  onCommentCode,
  onFindBugs,
  onOptimize,
  onGenerateTests,
  loading,
  code,
  setCode,
  error,
  commentedCode,
}) {
  return (
    <div className="page-container">
      <Header currentPage="home" onNavigate={onNavigate} />

      <main className="app-main">
        <div className="controls">
          <div className="controls-left">
            <div className="language-selector">
              <label htmlFor="language">Programming Language:</label>
              <select
                id="language"
                value={language}
                onChange={(e) => onLanguageChange(e.target.value)}
              >
                {supportedLanguages.map((lang) => (
                  <option key={lang.value} value={lang.value}>
                    {lang.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="action-buttons">
              <input
                type="file"
                ref={fileInputRef}
                onChange={onFileUpload}
                accept=".txt,.js,.jsx,.ts,.tsx,.py,.java,.cpp,.c,.cs,.php,.rb,.go,.rs,.swift,.kt,.scala,.clj,.sh,.sql,.html,.css,.json,.xml,.yaml,.yml"
                style={{ display: 'none' }}
              />
              <button
                onClick={() => fileInputRef && fileInputRef.current && fileInputRef.current.click()}
                className="btn btn-secondary"
              >
                📁 Upload File
              </button>
              <button
                onClick={onClearAll}
                className="btn btn-secondary"
              >
                🗑️ Clear All
              </button>
            </div>
          </div>

          <div className="controls-right">
            <div className="quick-actions">
              <div className="quick-action-buttons">
                <button
                  onClick={onCommentCode}
                  className="btn btn-quick-action"
                  disabled={loading || !code.trim()}
                  title="Add detailed comments to code"
                >
                  <span style={{ fontSize: '1rem', marginRight: '0.2rem' }}>💬</span>
                  Comment Code
                </button>
                <button
                  onClick={onFindBugs}
                  className="btn btn-quick-action"
                  disabled={loading || !code.trim()}
                  title="Find and fix bugs in code"
                >
                  <span style={{ fontSize: '1rem', marginRight: '0.2rem' }}>🐛</span>
                  Find Bugs
                </button>
                <button
                  onClick={onOptimize}
                  className="btn btn-quick-action"
                  disabled={loading || !code.trim()}
                  title="Optimize code performance"
                >
                  <span style={{ fontSize: '1rem', marginRight: '0.2rem' }}>⚡</span>
                  Optimize Code
                </button>
                <button
                  onClick={onGenerateTests}
                  className="btn btn-quick-action"
                  disabled={loading || !code.trim()}
                  title="Generate unit tests for code"
                >
                  <span style={{ fontSize: '1rem', marginRight: '0.2rem' }}>🧪</span>
                  Generate Tests
                </button>
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        <div className="code-sections">
          <div className="code-section">
            <h3>📥 Input</h3>
            <CodeEditor
              value={code}
              onChange={setCode}
              language={language}
              placeholder={`Enter or paste ${language} code here...`}
              rows={15}
            />
          </div>

          <div className="code-section">
            <h3>📤 Output</h3>
            {loading ? (
              <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Processing code with AI...</p>
              </div>
            ) : commentedCode ? (
              <div className="code-output">
                <SyntaxHighlighter
                  language={language}
                  style={tomorrow}
                  showLineNumbers={true}
                  wrapLines={true}
                >
                  {commentedCode}
                </SyntaxHighlighter>
              </div>
            ) : (
              <div className="placeholder">
                AI Assistant output will be displayed here...
              </div>
            )}
          </div>
        </div>
      </main>

      <HowToUse />
      <Footer />
    </div>
  );
}

export default HomePage;
