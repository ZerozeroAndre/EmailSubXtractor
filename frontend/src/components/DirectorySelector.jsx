import React, { useState } from 'react';
import { setOutputDirectory } from '../services/api';
import './DirectorySelector.css';

const DirectorySelector = ({ onDirectorySet }) => {
  const [directory, setDirectory] = useState('');
  const [status, setStatus] = useState('');

  const handleDirectoryPicker = async () => {
    try {
      // Show directory picker
      const dirHandle = await window.showDirectoryPicker();
      const dirPath = dirHandle.name;
      setDirectory(dirPath);
      
      // Set the selected directory
      const response = await setOutputDirectory(dirPath);
      setStatus(`Directory set successfully to: ${response.directory}`);
      if (onDirectorySet) {
        onDirectorySet(response.directory);
      }
    } catch (error) {
      if (error.name !== 'AbortError') { // Ignore if user cancelled
        setStatus(`Error: ${error.message}`);
      }
    }
  };

  return (
    <div className="directory-selector" role="region" aria-labelledby="directory-heading">
      <h3 id="directory-heading">Output Directory Settings</h3>
      <div className="directory-picker">
        <button 
          type="button" 
          onClick={handleDirectoryPicker}
          className="picker-button"
          aria-label="Choose Output Directory"
        >
          Choose Output Directory
        </button>
        {directory && (
          <div className="selected-directory" aria-live="polite">
            Selected: {directory}
          </div>
        )}
      </div>
      {status && <p className="status-message">{status}</p>}
    </div>
  );
};

export default DirectorySelector;