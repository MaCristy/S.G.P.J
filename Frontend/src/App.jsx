
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
import SolicitacoesCadastroPage from './pages/SolicitacoesCadastroPage.jsx';

import { useAuth } from './contexts/AuthContext.jsx';

// Controla o acesso às páginas que exigem autenticação e permissão.
function RotaProtegida({ children, perfisPermitidos = [] }) {
  const { isAuthenticated, loading, user } = useAuth();

  // Aguarda a verificação da sessão do usuário.
  if (loading) {
    return <p>Carregando...</p>;
  }

  // Redireciona visitantes para a tela de login.
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Verifica se o perfil possui autorização para acessar a página.
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
      {/* Páginas públicas, acessíveis sem autenticação. */}
      <Route element={<AppLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/cadastro" element={<CadastroPage />} />
        <Route
          path="/recuperar-senha"
          element={<RecuperarSenhaPage />}
        />
      </Route>

      {/* Dashboard do Aluno com seu próprio layout. */}
      <Route
        path="/dashboard/aluno"
        element={
          <RotaProtegida>
            <DashboardAlunoPage />
          </RotaProtegida>
        }
      />

      {/* Páginas internas que utilizam o layout compartilhado. */}
      <Route
        element={
          <RotaProtegida>
            <DashboardLayout />
          </RotaProtegida>
        }
      >
        <Route
          path="/assistidos"
          element={<AssistidosPage />}
        />

        {/* Área administrativa exclusiva da Gestão. */}
        <Route
          path="/solicitacoes-cadastro"
          element={
            <RotaProtegida perfisPermitidos={['Gestão']}>
              <SolicitacoesCadastroPage />
            </RotaProtegida>
          }
        />
      </Route>

      {/* Página apresentada para endereços inexistentes. */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
