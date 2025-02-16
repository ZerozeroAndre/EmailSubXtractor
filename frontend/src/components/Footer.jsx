// src/components/Footer.jsx
import React from 'react';
import './Footer.css';

function Footer() {
  return (
    <footer className="app-footer">
      <p>&copy; {new Date().getFullYear()} EmailSubXtractor</p>
    </footer>
  );
}

export default Footer;