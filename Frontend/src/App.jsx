
import { Navigate, Route, Routes } from 'react-router-dom';

import AppLayout from './layouts/AppLayout.jsx';
import DashboardLayout from './layouts/DashboardLayout.jsx';

import HomePage from './pages/HomePage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import CadastroPage from './pages/CadastroPage.jsx';
import NotFoundPage from './pages/NotFoundPage.jsx';
import RecuperarSenhaPage from './pages/RecuperarSenhaPage.jsx';

import DashboardAlunoPage from './pages/DashboardAlunoPage.jsx';
import DashboardProfessorPage from './pages/DashboardProfessorPage.jsx';
import AssistidosPage from './pages/AssistidosPage.jsx';
import SolicitacoesCadastroPage from './pages/SolicitacoesCadastroPage.jsx';
import AtendimentosPage from './pages/AtendimentosPage.jsx';
import CasosJuridicosPage from './pages/CasosJuridicosPage.jsx';
import AtividadesPage from './pages/AtividadesPage.jsx';
import PrazosPage from './pages/PrazosPage.jsx';
import HistoricoPage from './pages/HistoricoPage.jsx';
import DocumentosPage from './pages/DocumentosPage.jsx';

import { useAuth } from './contexts/AuthContext.jsx';

// Controla o acesso às páginas que exigem autenticação e permissão.
function RotaProtegida({ children, perfisPermitidos = [] }) {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) {
    return <p>Carregando...</p>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

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
      {/* Páginas públicas. */}
      <Route element={<AppLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/cadastro" element={<CadastroPage />} />
        <Route
          path="/recuperar-senha"
          element={<RecuperarSenhaPage />}
        />
      </Route>

      {/* Páginas internas com layout compartilhado. */}
      <Route
        element={
          <RotaProtegida>
            <DashboardLayout />
          </RotaProtegida>
        }
      >
        {/* Dashboard do Aluno. */}
        <Route
          path="/dashboard/aluno"
          element={
            <RotaProtegida perfisPermitidos={['Aluno']}>
              <DashboardAlunoPage />
            </RotaProtegida>
          }
        />

        {/* Dashboard do Professor. */}
        <Route
          path="/dashboard/professor"
          element={
            <RotaProtegida perfisPermitidos={['Professor']}>
              <DashboardProfessorPage />
            </RotaProtegida>
          }
        />

        {/* Área administrativa da Gestão. */}
        <Route
          path="/solicitacoes-cadastro"
          element={
            <RotaProtegida perfisPermitidos={['Gestão']}>
              <SolicitacoesCadastroPage />
            </RotaProtegida>
          }
        />

        {/* Assistidos. */}
        <Route
          path="/assistidos"
          element={<AssistidosPage />}
        />

        {/* Atendimentos. */}
        <Route
          path="/atendimentos"
          element={<AtendimentosPage />}
        />

        {/* Casos Jurídicos. */}
        <Route
          path="/casos-juridicos"
          element={<CasosJuridicosPage />}
        />

        {/* Atividades. */}
        <Route
          path="/atividades"
          element={<AtividadesPage />}
        />

        {/* Prazos. */}
        <Route
          path="/prazos"
          element={<PrazosPage />}
        />

        {/* Histórico. */}
        <Route
          path="/historico"
          element={<HistoricoPage />}
        />

        {/* Documentos. */}
        <Route
          path="/documentos"
          element={<DocumentosPage />}
        />
      </Route>

      {/* Página para endereços inexistentes. */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
