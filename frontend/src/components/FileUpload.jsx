// src/components/FileUpload.jsx
import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import './FileUpload.css';

function FileUpload({ onFileUpload, status }) {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0]);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: '.json'
  });

  return (
    <div className="file-upload">
      <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
        <input {...getInputProps()} />
        {isDragActive ? (
          <p>Drop the file here...</p>
        ) : (
          <p>Drag & drop your JSON file here, or click to select file</p>
        )}
      </div>
      {status && <p className="upload-status">{status}</p>}
    </div>
  );
}

export default FileUpload;