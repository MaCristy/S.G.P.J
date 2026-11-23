import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';

import App from './App.jsx';
import { AuthProvider } from './contexts/AuthContext.jsx';

import './styles/global.css';
import './styles/auth.css';

// Inicializa a aplicação React no elemento principal do HTML.
ReactDOM.createRoot(document.getElementById('root')).render(
  // Modo rigoroso para detectar problemas potenciais
  <React.StrictMode>
    {/* Disponibiliza o sistema de navegação entre as páginas. */}
    <BrowserRouter>
      {/* Compartilha os dados de autenticação com toda a aplicação. */}
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
