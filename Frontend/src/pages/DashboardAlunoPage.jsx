import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    LayoutDashboard,
    Users,
    ClipboardList,
    FolderOpen,
    CalendarClock,
    FileText,
    History,
    Bell,
    Search,
    UserCircle,
    Clock3,
    CheckCircle2,
    BriefcaseBusiness,
    Menu,
    LogOut
} from 'lucide-react';

const menuItems = [
    { label: 'Visão geral', icon: LayoutDashboard, active: true },
    { label: 'Assistidos', icon: Users },
    { label: 'Atendimentos', icon: ClipboardList },
    { label: 'Casos jurídicos', icon: FolderOpen },
    { label: 'Atividades', icon: BriefcaseBusiness },
    { label: 'Prazos', icon: CalendarClock },
    { label: 'Documentos', icon: FileText },
    { label: 'Histórico', icon: History },
];

const indicators = [
    {
        title: 'Casos atribuídos',
        value: '08',
        description: 'Casos sob sua responsabilidade',
        icon: FolderOpen,
        color: 'blue',
    },
    {
        title: 'Atividades pendentes',
        value: '05',
        description: 'Atividades aguardando conclusão',
        icon: ClipboardList,
        color: 'yellow',
    },
    {
        title: 'Prazos próximos',
        value: '03',
        description: 'Prazos que exigem atenção',
        icon: Clock3,
        color: 'orange',
    },
    {
        title: 'Atividades concluídas',
        value: '12',
        description: 'Atividades finalizadas',
        icon: CheckCircle2,
        color: 'green',
    },
];

const activities = [
    {
        title: 'Análise de documentação',
        caseName: 'Caso demonstrativo nº 001',
        date: '12/11/2026',
        status: 'Em andamento',
        statusClass: 'in-progress',
    },
    {
        title: 'Elaboração de relatório',
        caseName: 'Caso demonstrativo nº 002',
        date: '14/11/2026',
        status: 'Pendente',
        statusClass: 'pending',
    },
    {
        title: 'Revisão de atendimento',
        caseName: 'Caso demonstrativo nº 003',
        date: '16/11/2026',
        status: 'Concluída',
        statusClass: 'completed',
    },
];

const deadlines = [
    {
        day: '14',
        month: 'NOV',
        title: 'Entrega de relatório',
        description: 'Caso demonstrativo nº 002',
    },
    {
        day: '17',
        month: 'NOV',
        title: 'Revisão de documentação',
        description: 'Caso demonstrativo nº 001',
    },
    {
        day: '20',
        month: 'NOV',
        title: 'Atualização de andamento',
        description: 'Caso demonstrativo nº 003',
    },
];


export default function DashboardAlunoPage() {
    const [menuOpen, setMenuOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');

    const filteredActivities = activities.filter((activity) =>
        `${activity.title} ${activity.caseName} ${activity.status}`
            .toLowerCase()
            .includes(searchTerm.toLowerCase())
    );

    const filteredDeadlines = deadlines.filter((deadline) =>
        `${deadline.title} ${deadline.description} ${deadline.day} ${deadline.month}`
            .toLowerCase()
            .includes(searchTerm.toLowerCase())
    );

    const navigate = useNavigate();

    function handleMenuClick(item, event) {
        event.preventDefault();

        if (item === 'Assistidos') {
            navigate('/assistidos');
            return;
        }

        setMenuOpen(false);
    }
    return (
        <div className="dashboard-layout">
            {menuOpen && (
                <button
                    className="sidebar-overlay"
                    type="button"
                    aria-label="Fechar menu"
                    onClick={() => setMenuOpen(false)}
                />
            )}

            <aside className={`dashboard-sidebar ${menuOpen ? 'sidebar-open' : ''}`}>
                <div className="dashboard-brand">
                    <span className="dashboard-brand-mark">§</span>
                    <div>
                        <strong>S.G.P.J.</strong>
                        <small>Prática Jurídica</small>
                    </div>
                </div>


                <div className="sidebar-section-label">MENU PRINCIPAL</div>

                <nav className="dashboard-nav">
                    {menuItems.map(({ label, icon: Icon, active }) => (
                        <a
                            href="#"
                            key={label}
                            className={`dashboard-nav-item ${active ? 'active' : ''}`}
                            onClick={(event) => {
                                event.preventDefault();

                                if (label === 'Assistidos') {
                                    navigate('/assistidos');
                                    setMenuOpen(false);
                                    return;
                                }

                                setMenuOpen(false);
                            }}
                        >
                            <Icon size={19} />
                            <span>{label}</span>
                        </a>
                    ))}
                </nav>

                <div className="sidebar-bottom">
                    <div className="sidebar-help">
                        <ShieldCheckIcon />
                        <div>
                            <strong>Ambiente acadêmico</strong>
                            <small>Sistema de uso institucional</small>
                        </div>
                    </div>

                    <a href="/login" className="dashboard-logout">
                        <LogOut size={18} />
                        Sair do sistema
                    </a>
                </div>
            </aside>

            <main className="dashboard-main">
                <header className="dashboard-header">
                    <button
                        className="mobile-menu"
                        type="button"
                        aria-label={menuOpen ? 'Fechar menu' : 'Abrir menu'}
                        aria-expanded={menuOpen}
                        onClick={() => setMenuOpen(!menuOpen)}
                    >
                        <Menu size={21} />
                    </button>

                    <div className="dashboard-search">
                        <Search size={18} />
                        <input
                            type="search"
                            placeholder="Pesquisar atividades e prazos..."
                            aria-label="Pesquisar atividades e prazos"
                            value={searchTerm}
                            onChange={(event) => setSearchTerm(event.target.value)}
                        />
                    </div>

                    <div className="dashboard-header-actions">
                        <button type="button" className="notification-button" aria-label="Notificações">
                            <Bell size={20} />
                            <span />
                        </button>

                        <div className="dashboard-user">
                            <div className="user-avatar">
                                <UserCircle size={25} />
                            </div>
                            <div>
                                <strong>Aluno / Estagiário</strong>
                                <small>Área do estudante</small>
                            </div>
                        </div>
                    </div>
                </header>

                <div className="dashboard-content">
                    <section className="dashboard-welcome">
                        <div>
                            <span className="dashboard-eyebrow">ÁREA DO ALUNO</span>
                            <h1>Visão geral</h1>
                            <p>
                                Acompanhe seus casos jurídicos, atividades e prazos em um só lugar.
                            </p>
                        </div>

                        <div className="dashboard-date">
                            <CalendarClock size={18} />
                            <span>12 de novembro de 2026</span>
                        </div>
                    </section>

                    <section className="indicator-grid">
                        {indicators.map(({ title, value, description, icon: Icon, color }) => (
                            <article className="indicator-card" key={title}>
                                <div className={`indicator-icon ${color}`}>
                                    <Icon size={21} />
                                </div>
                                <div className="indicator-info">
                                    <span>{title}</span>
                                    <strong>{value}</strong>
                                    <small>{description}</small>
                                </div>
                            </article>
                        ))}
                    </section>

                    <section className="dashboard-panels">
                        <article className="dashboard-panel activities-panel">
                            <div className="panel-heading">
                                <div>
                                    <h2>Atividades recentes</h2>
                                    <p>Acompanhe suas últimas atividades.</p>
                                </div>
                                <button type="button" className="panel-link">
                                    Ver todas
                                </button>
                            </div>

                            <div className="activity-list">
                                {filteredActivities.length > 0 ? (
                                    filteredActivities.map((activity) => (
                                        <div className="activity-row" key={activity.title}>
                                            <div className="activity-symbol">
                                                <ClipboardList size={19} />
                                            </div>

                                            <div className="activity-description">
                                                <strong>{activity.title}</strong>
                                                <small>{activity.caseName}</small>
                                            </div>

                                            <span className={`activity-status ${activity.statusClass}`}>
                                                {activity.status}
                                            </span>
                                        </div>
                                    ))
                                ) : (
                                    <p className="search-empty">
                                        Nenhuma atividade encontrada.
                                    </p>
                                )}
                            </div>
                        </article>

                        <article className="dashboard-panel deadlines-panel">
                            <div className="panel-heading">
                                <div>
                                    <h2>Próximos prazos</h2>
                                    <p>Fique atento às datas.</p>
                                </div>
                                <CalendarClock size={20} className="panel-heading-icon" />
                            </div>

                            <div className="deadline-list">
                                {filteredDeadlines.length > 0 ? (
                                    filteredDeadlines.map((deadline) => (
                                        <div className="deadline-row" key={deadline.title}>
                                            <div className="deadline-date">
                                                <strong>{deadline.day}</strong>
                                                <span>{deadline.month}</span>
                                            </div>

                                            <div>
                                                <strong>{deadline.title}</strong>
                                                <small>{deadline.description}</small>
                                            </div>
                                        </div>
                                    ))
                                ) : (
                                    <p className="search-empty">
                                        Nenhum prazo encontrado.
                                    </p>
                                )}
                            </div>
                        </article>
                    </section>

                    <div className="dashboard-demo-notice">
                        <ShieldCheckIcon />
                        <p>
                            <strong>Ambiente demonstrativo:</strong> os indicadores, atividades
                            e prazos apresentados são dados ilustrativos. As informações reais
                            serão carregadas após a integração com o Backend.
                        </p>
                    </div>
                </div>
            </main>
        </div>
    );
}

function ShieldCheckIcon() {
    return <CheckCircle2 size={20} />;
}
