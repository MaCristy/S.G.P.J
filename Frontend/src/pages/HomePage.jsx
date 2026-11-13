import { ArrowRight, BookOpen, GraduationCap, ShieldCheck, Users } from 'lucide-react';
import { Link } from 'react-router-dom';

const profiles = [
  {
    icon: GraduationCap,
    title: 'Aluno / Estagiário',
    description: 'Área destinada ao acompanhamento dos casos, atividades e prazos atribuídos ao aluno.',
  },
  {
    icon: BookOpen,
    title: 'Professor / Orientador',
    description: 'Área de supervisão dos casos, orientação dos alunos e acompanhamento das atividades.',
  },
  {
    icon: Users,
    title: 'Gestão / Coordenação',
    description: 'Área administrativa para gestão de usuários e acompanhamento geral do sistema.',
  },
];

export default function HomePage() {
  return (
    <div className="home">
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow"><span className="eyebrow-dot" /> AMBIENTE DO SISTEMA</span>
          <h1>Gestão organizada.<br /><span>Prática jurídica eficiente.</span></h1>
          <p>
            Uma plataforma para apoiar a organização dos atendimentos, casos jurídicos,
            atividades e prazos da prática jurídica.
          </p>
          <div className="hero-note">
            <ShieldCheck size={18} />
            <span>Ambiente inicial do projeto — autenticação será integrada em etapa própria.</span>
          </div>
        </div>
        <div className="hero-illustration" aria-hidden="true">
          <div className="illustration-orbit orbit-one" />
          <div className="illustration-orbit orbit-two" />
          <div className="illustration-card">
            <div className="illustration-emblem">§</div>
            <div className="illustration-line line-long" />
            <div className="illustration-line line-short" />
            <div className="illustration-stat-row">
              <span /><span /><span />
            </div>
          </div>
          <div className="floating-icon"><BookOpen size={22} /></div>
          <div className="floating-icon floating-icon-bottom"><Users size={22} /></div>
        </div>
      </section>

      <section className="profiles-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">ESTRUTURA DE ACESSO</span>
            <h2>Perfis previstos no sistema</h2>
          </div>
          <p>As áreas e permissões serão definidas de acordo com o perfil autenticado.</p>
        </div>
        <div className="profile-grid">
          {profiles.map(({ icon: Icon, title, description }) => (
            <article className="profile-card" key={title}>
              <div className="profile-icon"><Icon size={22} /></div>
              <h3>{title}</h3>
              <p>{description}</p>
              <span className="planned-label">Área prevista</span>
            </article>
          ))}
        </div>
      </section>

      <div className="notice">
        <span className="notice-icon"><ShieldCheck size={19} /></span>
        <p><strong>Segurança e permissões:</strong> escolher um perfil em uma tela não concede privilégios.
          A autenticação e a autorização deverão ser verificadas pelo backend.</p>
      </div>
    </div>
  );
}