
import { Route, Routes } from 'react-router-dom';

import AppLayout from './layouts/AppLayout.jsx';
import DashboardLayout from './layouts/DashboardLayout.jsx';

import HomePage from './pages/HomePage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import CadastroPage from './pages/CadastroPage.jsx';
import NotFoundPage from './pages/NotFoundPage.jsx';
import RecuperarSenhaPage from './pages/RecuperarSenhaPage.jsx';

import DashboardAlunoPage from './pages/DashboardAlunoPage.jsx';
import AssistidosPage from './pages/AssistidosPage.jsx';

export default function App() {
  return (
    <Routes>
      {/* Páginas públicas */}
      <Route element={<AppLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/cadastro" element={<CadastroPage />} />
        <Route path="/recuperar-senha" element={<RecuperarSenhaPage />} />
      </Route>

      {/* Páginas internas do aluno */}
      <Route element={<DashboardLayout />}>
        <Route
          path="/dashboard/aluno"
          element={<DashboardAlunoPage />}
        />

        <Route
          path="/assistidos"
          element={<AssistidosPage />}
        />
      </Route>

      {/* Página não encontrada */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
