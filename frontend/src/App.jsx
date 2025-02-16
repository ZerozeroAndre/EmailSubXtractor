// src/App.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import EmailList from './components/EmailList';
import Footer from './components/Footer';
import './App.css';

function App() {
  const [processedEmails, setProcessedEmails] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [outputFiles, setOutputFiles] = useState({ processed: null, analytics: null });
  const [outputDirectory] = useState("/default/output/directory");

  const handleFileUpload = async (file) => {
    if (!file) return;
    setUploadStatus("Uploading...");
    const formData = new FormData();
    formData.append("file", file);
    try {
      const response = await axios.post("http://localhost:8000/process-emails", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      
      if (response.data.status === "success") {
        setProcessedEmails(response.data.data);
        // Get the output file paths
        const timestamp = new Date().toISOString().replace(/[:.]/g, "").slice(0, 15);
        setOutputFiles({
          processed: `processed_emails_${timestamp}.json`,
          analytics: `analytics_${timestamp}.json`
        });
        setUploadStatus("Processing complete! Files have been saved.");
      } else {
        throw new Error("Processing failed");
      }
    } catch (error) {
      console.error("Error processing file:", error);
      setUploadStatus(
        error.response?.data?.detail || 
        error.message || 
        "Error processing file. Please ensure your JSON file contains a list of email objects."
      );
    }
  };

  const fetchAnalytics = async () => {
    try {
      const res = await axios.get("http://localhost:8000/analytics");
      setAnalytics(res.data);
    } catch (error) {
      console.error("Error fetching analytics:", error);
    }
  };

  // Fetch analytics when processed emails change.
  useEffect(() => {
    if (processedEmails.length > 0) {
      fetchAnalytics();
    }
  }, [processedEmails]);

  return (
    <div className="App">
      <Header title="Email Subscription Extractor" />
      <div className="container">
        <FileUpload onFileUpload={handleFileUpload} status={uploadStatus} />
        {outputFiles.processed && (
          <div className="output-files">
            <h3>Output Files:</h3>
            <p>Results saved to directory: {outputDirectory}</p>
            <ul>
              <li>Processed emails: {outputFiles.processed}</li>
              <li>Analytics data: {outputFiles.analytics}</li>
            </ul>
          </div>
        )}
        <AnalyticsDashboard analytics={analytics} />
        <EmailList emails={processedEmails} />
      </div>
      <Footer />
    </div>
  );
}

export default App;