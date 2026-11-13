
import { useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
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
    BriefcaseBusiness,
    Menu,
    LogOut,
    CheckCircle2,
} from 'lucide-react';

const menuItems = [
    { label: 'Visão geral', icon: LayoutDashboard, path: '/dashboard/aluno' },
    { label: 'Assistidos', icon: Users, path: '/assistidos' },
    { label: 'Atendimentos', icon: ClipboardList },
    { label: 'Casos jurídicos', icon: FolderOpen },
    { label: 'Atividades', icon: BriefcaseBusiness },
    { label: 'Prazos', icon: CalendarClock },
    { label: 'Documentos', icon: FileText },
    { label: 'Histórico', icon: History },
];

export default function DashboardLayout() {
    const [menuOpen, setMenuOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');

    const navigate = useNavigate();
    const location = useLocation();

    const isDashboard = location.pathname === '/dashboard/aluno';

    function handleMenuClick(item) {
        if (item.path) {
            navigate(item.path);
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
                    {menuItems.map(({ label, icon: Icon, path }) => (
                        <a
                            href={path || '#'}
                            key={label}
                            className={`dashboard-nav-item ${path && location.pathname === path ? 'active' : ''
                                }`}
                            onClick={(event) => {
                                event.preventDefault();
                                handleMenuClick({ label, path });
                            }}
                        >
                            <Icon size={19} />
                            <span>{label}</span>
                        </a>
                    ))}
                </nav>

                <div className="sidebar-bottom">
                    <div className="sidebar-help">
                        <CheckCircle2 size={20} />
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

                    {isDashboard && (
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
                    )}

                    <div className="dashboard-header-actions">
                        <button
                            type="button"
                            className="notification-button"
                            aria-label="Notificações"
                        >
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
                    <Outlet context={{ searchTerm }} />
                </div>
            </main>
        </div>
    );
}
