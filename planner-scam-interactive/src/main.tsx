import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/global.css';
import './styles/animations.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// remove the pre-react boot splash
window.addEventListener('load', () => {
  const splash = document.getElementById('boot-splash');
  if (splash) {
    splash.style.opacity = '0';
    setTimeout(() => splash.remove(), 450);
  }
});
