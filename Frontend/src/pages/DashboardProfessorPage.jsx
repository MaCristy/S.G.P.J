
import { useEffect, useState } from 'react';
import {
    ClipboardList,
    FolderOpen,
    Users,
    CalendarClock,
    BookOpenCheck,
    Clock3,
} from 'lucide-react';

import { buscarDashboardProfessor } from '../services/dashboardService';

function formatarData(data) {
    if (!data) return 'Sem data';

    const dataLocal = new Date(`${data}T00:00:00`);

    if (Number.isNaN(dataLocal.getTime())) return 'Sem data';

    return dataLocal.toLocaleDateString('pt-BR');
}

function classeSituacao(situacao) {
    const status = situacao?.toLowerCase();

    if (status === 'concluída' || status === 'concluido') {
        return 'completed';
    }

    if (status === 'em andamento') {
        return 'in-progress';
    }

    return 'pending';
}

export default function DashboardProfessorPage() {
    const [dashboard, setDashboard] = useState(null);
    const [carregando, setCarregando] = useState(true);
    const [erro, setErro] = useState('');

    useEffect(() => {
        async function carregarDashboard() {
            try {
                setCarregando(true);
                setErro('');

                const dados = await buscarDashboardProfessor();
                setDashboard(dados);
            } catch (error) {
                setErro(error.message || 'Não foi possível carregar a visão geral.');
            } finally {
                setCarregando(false);
            }
        }

        carregarDashboard();
    }, []);

    const indicadores = [
        {
            title: 'Casos jurídicos',
            value: dashboard?.total_casos ?? 0,
            description: 'Casos sob sua orientação',
            icon: FolderOpen,
            color: 'blue',
        },
        {
            title: 'Alunos',
            value: dashboard?.total_alunos ?? 0,
            description: 'Estudantes vinculados',
            icon: Users,
            color: 'yellow',
        },
        {
            title: 'Atividades',
            value: dashboard?.total_atividades ?? 0,
            description: 'Atividades dos casos',
            icon: ClipboardList,
            color: 'orange',
        },
        {
            title: 'Prazos próximos',
            value: dashboard?.total_prazos_proximos ?? 0,
            description: 'Prazos que exigem atenção',
            icon: CalendarClock,
            color: 'green',
        },
    ];

    const atividades = dashboard?.atividades_recentes ?? [];
    const prazos = dashboard?.prazos_proximos ?? [];

    return (
        <div className="dashboard-content">
            <section className="dashboard-welcome">
                <div>
                    <span className="dashboard-eyebrow">
                        ÁREA DO PROFESSOR
                    </span>

                    <h1>Visão geral</h1>

                    <p>
                        Acompanhe os casos jurídicos, os alunos orientados
                        e as atividades relacionadas à prática jurídica.
                    </p>
                </div>

                <div className="dashboard-date">
                    <CalendarClock size={18} />
                    <span>Área de orientação acadêmica</span>
                </div>
            </section>

            {erro && (
                <div className="dashboard-demo-notice">
                    <p>
                        <strong>Não foi possível carregar os dados:</strong> {erro}
                    </p>
                </div>
            )}

            <section className="indicator-grid">
                {indicadores.map(({ title, value, description, icon: Icon, color }) => (
                    <article className="indicator-card" key={title}>
                        <div className={`indicator-icon ${color}`}>
                            <Icon size={21} />
                        </div>

                        <div className="indicator-info">
                            <span>{title}</span>
                            <strong>{carregando ? '...' : value}</strong>
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
                            <p>
                                Atividades dos casos sob sua orientação.
                            </p>
                        </div>

                        <BookOpenCheck
                            size={22}
                            className="panel-heading-icon"
                        />
                    </div>

                    <div className="activity-list">
                        {carregando ? (
                            <p className="search-empty">
                                Carregando atividades...
                            </p>
                        ) : atividades.length > 0 ? (
                            atividades.map((atividade) => (
                                <div
                                    className="activity-row"
                                    key={atividade.id_atividade}
                                >
                                    <div className="activity-symbol">
                                        <ClipboardList size={19} />
                                    </div>

                                    <div className="activity-description">
                                        <strong>{atividade.titulo}</strong>
                                        <small>{atividade.codigo_caso}</small>
                                        <small>
                                            {formatarData(atividade.data_prevista)}
                                        </small>
                                    </div>

                                    <span
                                        className={`activity-status ${classeSituacao(atividade.situacao)}`}
                                    >
                                        {atividade.situacao}
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
                            <p>
                                Prazos dos casos sob sua orientação.
                            </p>
                        </div>

                        <Clock3
                            size={22}
                            className="panel-heading-icon"
                        />
                    </div>

                    <div className="deadline-list">
                        {carregando ? (
                            <p className="search-empty">
                                Carregando prazos...
                            </p>
                        ) : prazos.length > 0 ? (
                            prazos.map((prazo) => {
                                const data = prazo.data_limite
                                    ? new Date(`${prazo.data_limite}T00:00:00`)
                                    : null;

                                return (
                                    <div
                                        className="deadline-row"
                                        key={prazo.id_prazo}
                                    >
                                        <div className="deadline-date">
                                            <strong>
                                                {data && !Number.isNaN(data.getTime())
                                                    ? String(data.getDate()).padStart(2, '0')
                                                    : '--'}
                                            </strong>

                                            <span>
                                                {data && !Number.isNaN(data.getTime())
                                                    ? data.toLocaleDateString('pt-BR', {
                                                        month: 'short',
                                                    }).replace('.', '').toUpperCase()
                                                    : '---'}
                                            </span>
                                        </div>

                                        <div>
                                            <strong>{prazo.descricao}</strong>
                                            <small>{prazo.codigo_caso}</small>
                                            <small>
                                                {formatarData(prazo.data_limite)}
                                            </small>
                                        </div>
                                    </div>
                                );
                            })
                        ) : (
                            <p className="search-empty">
                                Nenhum prazo próximo encontrado.
                            </p>
                        )}
                    </div>
                </article>
                <section className="dashboard-panel">
                    <div className="panel-heading">
                        <div>
                            <h2>Acompanhamento acadêmico</h2>
                            <p>
                                Recursos de supervisão da prática jurídica.
                            </p>
                        </div>

                        <BookOpenCheck
                            size={22}
                            className="panel-heading-icon"
                        />
                    </div>

                    <div className="academic-monitoring-grid">
                        <div className="academic-monitoring-item">
                            <FolderOpen size={22} />
                            <div>
                                <strong>Supervisão de casos</strong>
                                <p>Acompanhe os casos sob sua orientação.</p>
                            </div>
                        </div>

                        <div className="academic-monitoring-item">
                            <Users size={22} />
                            <div>
                                <strong>Acompanhamento de alunos</strong>
                                <p>Consulte as atividades dos estudantes vinculados.</p>
                            </div>
                        </div>

                        <div className="academic-monitoring-item">
                            <CalendarClock size={22} />
                            <div>
                                <strong>Controle de prazos</strong>
                                <p>Monitore datas e pendências dos casos.</p>
                            </div>
                        </div>
                    </div>
                </section>

                {!carregando && !erro && (
                    <div className="dashboard-demo-notice">
                        <BookOpenCheck size={20} />

                        <p>
                            <strong>Dados atualizados:</strong> os indicadores,
                            atividades e prazos são carregados a partir dos
                            registros dos casos sob sua orientação.
                        </p>
                    </div>
                )}
            </section>
        </div>
    );
}
