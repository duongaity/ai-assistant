import React from 'react';
import './Header.css';

function Header({ currentPage, onNavigate }) {
  return (
    <header className="app-header">
      <div className="header-content">
        <div className="header-main">
          <h1>🤖 AI Programming Assistant</h1>
          <p>Smart programming support with AI - Comment code, Debug, Optimize & More</p>
        </div>
      </div>
      <nav className="header-nav">
        <button 
          onClick={() => onNavigate('home')}
          className={`nav-btn ${currentPage === 'home' ? 'active' : ''}`}
        >
          🏠 Home
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
