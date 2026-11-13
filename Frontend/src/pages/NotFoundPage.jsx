import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <section className="not-found">
      <span className="eyebrow">ERRO 404</span>
      <h1>Página não encontrada</h1>
      <p>O endereço acessado não corresponde a uma página disponível.</p>
      <Link className="primary-link" to="/">Voltar ao início</Link>
    </section>
  );
}