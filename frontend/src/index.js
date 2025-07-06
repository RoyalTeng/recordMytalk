import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// 引入TDesign样式
import 'tdesign-react/es/style/index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
); 