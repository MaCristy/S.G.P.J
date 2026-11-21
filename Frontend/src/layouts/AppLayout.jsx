
import { Outlet } from 'react-router-dom';

// Define a estrutura compartilhada das páginas públicas.
export default function AppLayout() {
  // Renderiza a página correspondente à rota acessada.
  return <Outlet />;
}
