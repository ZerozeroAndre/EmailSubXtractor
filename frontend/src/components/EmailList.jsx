// src/components/EmailList.jsx
import React from 'react';
import './EmailList.css';

function EmailList({ emails }) {
  if (!emails || emails.length === 0) return <p>No emails processed.</p>;

  return (
    <div className="email-list">
      <h2>Processed Emails</h2>
      {emails.map((email, index) => (
        <div key={index} className="email-card">
          <h3>{email.subject}</h3>
          <p><strong>Body Length:</strong> {email.body_length}</p>
          <div className="subscription-info">
            <h4>Subscription Info:</h4>
            <pre>{JSON.stringify(email.subscription_info, null, 2)}</pre>
          </div>
        </div>
      ))}
    </div>
  );
}

export default EmailList;