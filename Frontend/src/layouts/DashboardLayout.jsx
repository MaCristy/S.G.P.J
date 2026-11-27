
import { useEffect, useState } from 'react';
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
    UserPlus,
} from 'lucide-react';
import {
    listarNotificacoes,
    contarNotificacoesNaoLidas,
    marcarNotificacaoComoLida,
} from '../services/notificacaoService.js';

import { useAuth } from '../contexts/AuthContext.jsx';

// Padroniza o perfil para reconhecer nomes com ou sem acentuação.
function normalizarPerfil(perfil) {
    return (perfil || '')
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase();
}

export default function DashboardLayout() {
    // Controla a abertura e o fechamento do menu lateral.
    const [menuOpen, setMenuOpen] = useState(false);

    // Armazena o texto digitado na pesquisa.
    const [searchTerm, setSearchTerm] = useState('');

    // Armazena as notificações do usuário autenticado.
    const [notificacoes, setNotificacoes] = useState([]);

    // Armazena a quantidade de notificações ainda não lidas.
    const [totalNaoLidas, setTotalNaoLidas] = useState(0);

    // Controla a abertura e o fechamento do painel de notificações.
    const [notificacoesAbertas, setNotificacoesAbertas] = useState(false);

    // Busca as notificações e atualiza o contador do sino.
    async function carregarNotificacoes() {
        try {
            const [lista, quantidade] = await Promise.all([
                listarNotificacoes(),
                contarNotificacoesNaoLidas(),
            ]);

            setNotificacoes(lista || []);
            setTotalNaoLidas(quantidade?.total || 0);
        } catch (erro) {
            console.error('Erro ao carregar notificações:', erro);
        }
    }

    // Marca uma notificação como lida e atualiza o contador.
    async function handleMarcarComoLida(idNotificacao) {
        try {
            await marcarNotificacaoComoLida(idNotificacao);

            await carregarNotificacoes();
        } catch (erro) {
            console.error('Erro ao marcar notificação como lida:', erro);
        }
    }

    // Abre ou fecha o painel de notificações.
    async function handleToggleNotificacoes() {
        const abrir = !notificacoesAbertas;

        setNotificacoesAbertas(abrir);

        if (abrir) {
            await carregarNotificacoes();
        }
    }

    // Carrega as notificações assim que o painel é aberto.
    useEffect(() => {
        carregarNotificacoes();
    }, []);

    const navigate = useNavigate();
    const location = useLocation();

    // Recupera os dados do usuário autenticado.
    const { user } = useAuth();

    // Identifica o perfil do usuário.
    const perfil = normalizarPerfil(user?.perfil);
    const ehGestao = perfil === 'gestao';

    // Define os dados de identificação apresentados no cabeçalho.
    const identificacaoPerfil = {
        gestao: {
            titulo: 'Gestão / Coordenação',
            subtitulo: 'Área administrativa',
        },
        professor: {
            titulo: 'Professor / Orientador',
            subtitulo: 'Área docente',
        },
        aluno: {
            titulo: 'Aluno / Estagiário',
            subtitulo: 'Área do estudante',
        },
    };

    const dadosPerfil = identificacaoPerfil[perfil] || {
        titulo: 'Usuário',
        subtitulo: 'Área do sistema',
    };

    // Define a página inicial de acordo com o perfil autenticado.
    const rotaInicial = {
        gestao: '/solicitacoes-cadastro',
        professor: '/dashboard/professor',
        aluno: '/dashboard/aluno',
    };

    // Define o nome e o destino da primeira opção do menu.
    const itemInicial = {
        label: ehGestao ? 'Solicitações de cadastro' : 'Visão geral',
        icon: ehGestao ? UserPlus : LayoutDashboard,
        path: rotaInicial[perfil],
    };

    // Define as opções de navegação compartilhadas entre os perfis.
    const menuItems = [
        itemInicial,
        { label: 'Assistidos', icon: Users, path: '/assistidos' },
        { label: 'Atendimentos', icon: ClipboardList, path: '/atendimentos' },
        { label: 'Casos jurídicos', icon: FolderOpen, path: '/casos-juridicos' },
        { label: 'Atividades', icon: ClipboardList, path: '/atividades' },
        { label: 'Prazos', icon: CalendarClock, path: '/prazos' },
        { label: 'Documentos', icon: FileText, path: '/documentos' },
        { label: 'Histórico', icon: History, path: '/historico' },
    ];

    // Identifica se o usuário está em uma das páginas de dashboard.
    const isDashboard = [
        '/dashboard/aluno',
        '/dashboard/professor',
    ].includes(location.pathname);

    // Realiza a navegação e fecha o menu após a seleção.
    function handleMenuClick(item) {
        if (item.path) {
            navigate(item.path);
        }

        setMenuOpen(false);
    }

    return (
        <div className="dashboard-layout">
            {/* Sobreposição utilizada para fechar o menu em telas menores. */}
            {menuOpen && (
                <button
                    className="sidebar-overlay"
                    type="button"
                    aria-label="Fechar menu"
                    onClick={() => setMenuOpen(false)}
                />
            )}

            {/* Menu lateral de navegação do sistema. */}
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

                {/* Informações institucionais e opção de saída. */}
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

            {/* Área principal que contém o cabeçalho e o conteúdo das páginas. */}
            <main className="dashboard-main">
                <header className="dashboard-header">
                    {/* Botão de controle do menu para dispositivos móveis. */}
                    <button
                        className="mobile-menu"
                        type="button"
                        aria-label={menuOpen ? 'Fechar menu' : 'Abrir menu'}
                        aria-expanded={menuOpen}
                        onClick={() => setMenuOpen(!menuOpen)}
                    >
                        <Menu size={21} />
                    </button>

                    {/* Exibe a pesquisa somente nas páginas de dashboard. */}
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
                        {/* Botão de notificações. */}
                        <button
                            type="button"
                            className="notification-button"
                            aria-label="Notificações"
                            aria-expanded={notificacoesAbertas}
                            onClick={handleToggleNotificacoes}
                        >
                            <Bell size={20} />

                            {totalNaoLidas > 0 && (
                                <span>
                                    {totalNaoLidas > 9 ? '9+' : totalNaoLidas}
                                </span>
                            )}
                        </button>
                        {notificacoesAbertas && (
                            <div className="notifications-panel">
                                <div className="notifications-header">
                                    <strong>Notificações</strong>

                                    <button
                                        type="button"
                                        onClick={() => setNotificacoesAbertas(false)}
                                        aria-label="Fechar notificações"
                                    >
                                        ×
                                    </button>
                                </div>

                                <div className="notifications-list">
                                    {notificacoes.length === 0 ? (
                                        <p className="notifications-empty">
                                            Você não possui notificações.
                                        </p>
                                    ) : (
                                        notificacoes.map((notificacao) => (
                                            <div
                                                key={notificacao.id_notificacao}
                                                className={`notification-item ${notificacao.lida ? 'read' : 'unread'
                                                    }`}
                                            >
                                                <div className="notification-content">
                                                    <strong>{notificacao.titulo}</strong>

                                                    <p>{notificacao.mensagem}</p>

                                                    <small>
                                                        {new Date(
                                                            notificacao.data_criacao
                                                        ).toLocaleString('pt-BR')}
                                                    </small>
                                                </div>

                                                {!notificacao.lida && (
                                                    <button
                                                        type="button"
                                                        onClick={() =>
                                                            handleMarcarComoLida(
                                                                notificacao.id_notificacao
                                                            )
                                                        }
                                                    >
                                                        Marcar como lida
                                                    </button>
                                                )}
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        )}

                        {/* Apresenta a identificação correspondente ao perfil autenticado. */}
                        <div className="dashboard-user">
                            <div className="user-avatar">
                                <UserCircle size={25} />
                            </div>
                            <div>
                                <strong>{user?.nome || 'Usuário'}</strong>
                                <small>{dadosPerfil.titulo}</small>
                            </div>
                        </div>
                    </div>
                </header>

                {/* Renderiza a página interna e disponibiliza o termo de pesquisa. */}
                <div className="dashboard-content">
                    <Outlet context={{ searchTerm }} />
                </div>
            </main>
        </div>
    );
}
