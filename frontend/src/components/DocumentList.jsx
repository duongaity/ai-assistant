import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './DocumentList.css';

const API_BASE_URL = 'http://localhost:8888/api';

function DocumentList({ selectedFiles, onFileSelection, refreshTrigger }) {
  const [availableFiles, setAvailableFiles] = useState([]);

  // Load danh sách files khi component mount hoặc khi refreshTrigger thay đổi
  useEffect(() => {
    loadAvailableFiles();
  }, [refreshTrigger]);

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

  const handleSelectAll = () => {
    const allFileIds = availableFiles?.map(file => file.file_id) || [];
    if (onFileSelection) {
      onFileSelection(allFileIds);
    }
  };

  const handleDeselectAll = () => {
    if (onFileSelection) {
      onFileSelection([]);
    }
  };

  const handleFileToggle = (fileId) => {
    if (!onFileSelection || !selectedFiles) return;
    
    const newSelectedFiles = selectedFiles.includes(fileId)
      ? selectedFiles.filter(id => id !== fileId)
      : [...selectedFiles, fileId];
    
    onFileSelection(newSelectedFiles);
  };

  return (
    <div className="file-list-section">
      <h3>📚 Document List ({availableFiles?.length || 0})</h3>
      {availableFiles && availableFiles.length > 0 ? (
        <div className="file-list">
          <div className="select-all-controls">
            <button 
              className="select-button"
              onClick={handleSelectAll}
            >
              Select All
            </button>
            <button 
              className="select-button"
              onClick={handleDeselectAll}
            >
              Deselect All
            </button>
          </div>
          
          <div className="files-list">
            {availableFiles && availableFiles.map((file) => (
              <div 
                key={file.file_id} 
                className={`file-item ${selectedFiles?.includes(file.file_id) ? 'selected' : ''}`}
                onClick={() => handleFileToggle(file.file_id)}
              >
                <div className="file-checkbox">
                  <input
                    type="checkbox"
                    checked={selectedFiles?.includes(file.file_id) || false}
                    onChange={() => handleFileToggle(file.file_id)}
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
  );
}

export default DocumentList;
