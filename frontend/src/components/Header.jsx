import React from 'react';
import './Header.css';

function Header({ currentPage, onNavigate }) {
  const getHeaderContent = () => {
    if (currentPage === 'knowledge-base') {
      return {
        title: '📚 Knowledge Base',
        subtitle: 'A knowledge base is a centralized hub where teams can quickly find answers, troubleshoot issues, and access resources.'
      };
    }
    return {
      title: '🤖 AI Programming Assistant',
      subtitle: 'AI-powered programming support enhances this by automating code commenting, debugging, optimization and more.'
    };
  };

  const headerContent = getHeaderContent();

  return (
    <header className="app-header">
      <div className="header-content">
        <div className="header-main">
          <h1>{headerContent.title}</h1>
          <p>{headerContent.subtitle}</p>
        </div>
      </div>
      <nav className="header-nav">
        <button 
          onClick={() => onNavigate('home')}
          className={`nav-btn ${currentPage === 'home' ? 'active' : ''}`}
        >
          🏠 Home Page
        </button>
        <button 
          onClick={() => onNavigate('knowledge-base')}
          className={`nav-btn ${currentPage === 'knowledge-base' ? 'active' : ''}`}
        >
          📚 Knowledge Base
        </button>
      </nav>
    </header>
  );
}

export default Header;
