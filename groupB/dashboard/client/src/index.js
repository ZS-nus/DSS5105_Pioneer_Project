import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import reportWebVitals from './reportWebVitals';
import Login from './login'; // Renamed to follow React's convention

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Login /> {/* Correctly using the Login component */}
  </React.StrictMode>
);

reportWebVitals();