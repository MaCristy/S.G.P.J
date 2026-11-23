
import { Navigate, Route, Routes } from 'react-router-dom';

import AppLayout from './layouts/AppLayout.jsx';
import DashboardLayout from './layouts/DashboardLayout.jsx';

import HomePage from './pages/HomePage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import CadastroPage from './pages/CadastroPage.jsx';
import NotFoundPage from './pages/NotFoundPage.jsx';
import RecuperarSenhaPage from './pages/RecuperarSenhaPage.jsx';

import DashboardAlunoPage from './pages/DashboardAlunoPage.jsx';
import AssistidosPage from './pages/AssistidosPage.jsx';

import { useAuth } from './contexts/AuthContext.jsx';

// Controla o acesso às páginas que exigem autenticação.
function RotaProtegida({ children, perfisPermitidos = [] }) {
  const { isAuthenticated, loading, user } = useAuth();

  // Aguarda a verificação da sessão antes de liberar ou bloquear o acesso.
  if (loading) {
    return <p>Carregando...</p>;
  }

  // Redireciona para o login quando não existe uma sessão autenticada.
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Impede o acesso quando o perfil não possui a permissão necessária.
  if (
    perfisPermitidos.length > 0 &&
    !perfisPermitidos.includes(user?.perfil)
  ) {
    return <Navigate to="/" replace />;
  }

  return children;
}

export default function App() {
  return (
    <Routes>
      {/* Páginas públicas e cadastro administrativo. */}
      <Route element={<AppLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/recuperar-senha" element={<RecuperarSenhaPage />} />

        {/* Permite o cadastro de usuários somente ao perfil Gestão. */}
        <Route
          path="/cadastro"
          element={
            <RotaProtegida perfisPermitidos={['Gestão']}>
              <CadastroPage />
            </RotaProtegida>
          }
        />
      </Route>

      {/* Páginas internas que exigem autenticação. */}
      <Route
        element={
          <RotaProtegida>
            <DashboardLayout />
          </RotaProtegida>
        }
      >
        <Route
          path="/dashboard/aluno"
          element={<DashboardAlunoPage />}
        />

        <Route
          path="/assistidos"
          element={<AssistidosPage />}
        />
      </Route>

      {/* Exibe a página de erro para rotas inexistentes. */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
