import React, { useState } from 'react';
import axios from 'axios';
import './DocumentUpload.css';

const API_BASE_URL = 'http://localhost:8888/api';

function DocumentUpload({ onUploadSuccess, onMessage }) {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploading, setUploading] = useState(false);

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
        const message = `Great! I've received the file "${uploadedFile.name}" with ID: ${response.data.file_id}. You can now ask me about the content of this file.`;
        
        // Notify parent components
        if (onMessage) {
          onMessage(message);
        }
        if (onUploadSuccess) {
          onUploadSuccess(response.data);
        }
        
        // Reset uploaded file
        setUploadedFile(null);
        document.getElementById('file-upload').value = '';
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

  return (
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
  );
}

export default DocumentUpload;
