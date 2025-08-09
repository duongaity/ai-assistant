import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './KnowledgeBasePage.css';

function KnowledgeBasePage({ onNavigate }) {
  return (
    <div className="page-container">
      <Header currentPage="knowledge-base" onNavigate={onNavigate} />
      
      <main className="knowledge-base-main">
        <div className="knowledge-base-container">
          <h2>📚 Knowledge Base</h2>
          <p>Welcome to the AI Programming Assistant Knowledge Base</p>
          
          <div className="knowledge-sections">
            <div className="knowledge-section">
              <h3>🚀 Getting Started</h3>
              <p>Learn how to use the AI Programming Assistant effectively.</p>
              <ul>
                <li>Upload your code files or paste code directly</li>
                <li>Select the appropriate programming language</li>
                <li>Use Quick Actions for instant code analysis</li>
                <li>Chat with AI for detailed explanations</li>
              </ul>
            </div>
            
            <div className="knowledge-section">
              <h3>💡 Programming Tips</h3>
              <p>Best practices and tips for various programming languages.</p>
              <ul>
                <li>Write clean and readable code</li>
                <li>Use meaningful variable names</li>
                <li>Comment your code properly</li>
                <li>Follow language-specific conventions</li>
              </ul>
            </div>
            
            <div className="knowledge-section">
              <h3>🔧 Features</h3>
              <p>Explore all the features available in the AI Assistant.</p>
              <ul>
                <li><strong>Comment Code:</strong> Add detailed Vietnamese comments</li>
                <li><strong>Find Bugs:</strong> Identify and fix code issues</li>
                <li><strong>Optimize:</strong> Improve code performance</li>
                <li><strong>Generate Tests:</strong> Create unit tests automatically</li>
                <li><strong>AI Chat:</strong> Interactive programming assistance</li>
              </ul>
            </div>
            
            <div className="knowledge-section">
              <h3>❓ FAQ</h3>
              <p>Frequently asked questions and their answers.</p>
              <div className="faq-item">
                <h4>Q: What programming languages are supported?</h4>
                <p>A: We support Java, Python, JavaScript, TypeScript, C++, C#, PHP, Ruby, Go, Rust, Swift, Kotlin, Scala, and many more.</p>
              </div>
              <div className="faq-item">
                <h4>Q: How accurate is the AI analysis?</h4>
                <p>A: Our AI provides high-quality suggestions based on best practices and common patterns, but always review the output.</p>
              </div>
              <div className="faq-item">
                <h4>Q: Can I upload multiple files?</h4>
                <p>A: Currently, you can upload one file at a time or paste code directly into the editor.</p>
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
