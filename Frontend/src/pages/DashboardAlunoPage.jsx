
import { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
    ClipboardList,
    FolderOpen,
    CalendarClock,
    Clock3,
    CheckCircle2,
} from 'lucide-react';

import { buscarDashboardAluno } from '../services/dashboardService';

function formatarData(data) {
    if (!data) return 'Sem data';

    const dataLocal = new Date(`${data}T00:00:00`);

    if (Number.isNaN(dataLocal.getTime())) return 'Sem data';

    return dataLocal.toLocaleDateString('pt-BR');
}

function formatarDataExtenso(data = new Date()) {
    return data.toLocaleDateString('pt-BR', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
    });
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

export default function DashboardAlunoPage() {
    const outletContext = useOutletContext();
    const searchTerm = outletContext?.searchTerm ?? '';

    const [dashboard, setDashboard] = useState(null);
    const [carregando, setCarregando] = useState(true);
    const [erro, setErro] = useState('');

    useEffect(() => {
        async function carregarDashboard() {
            try {
                setCarregando(true);
                setErro('');

                const dados = await buscarDashboardAluno();
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
            title: 'Casos atribuídos',
            value: dashboard?.total_casos ?? 0,
            description: 'Casos sob sua responsabilidade',
            icon: FolderOpen,
            color: 'blue',
        },
        {
            title: 'Atividades pendentes',
            value: dashboard?.total_atividades_pendentes ?? 0,
            description: 'Atividades aguardando conclusão',
            icon: ClipboardList,
            color: 'yellow',
        },
        {
            title: 'Prazos próximos',
            value: dashboard?.total_prazos_proximos ?? 0,
            description: 'Prazos que exigem atenção',
            icon: Clock3,
            color: 'orange',
        },
        {
            title: 'Atividades concluídas',
            value: dashboard?.total_atividades_concluidas ?? 0,
            description: 'Atividades finalizadas',
            icon: CheckCircle2,
            color: 'green',
        },
    ];

    const atividades = dashboard?.atividades_recentes ?? [];
    const prazos = dashboard?.prazos_proximos ?? [];

    const atividadesFiltradas = atividades.filter((atividade) =>
        `${atividade.titulo} ${atividade.codigo_caso} ${atividade.situacao}`
            .toLowerCase()
            .includes(searchTerm.toLowerCase())
    );

    const prazosFiltrados = prazos.filter((prazo) =>
        `${prazo.descricao} ${prazo.codigo_caso} ${prazo.data_limite}`
            .toLowerCase()
            .includes(searchTerm.toLowerCase())
    );

    return (
        <>
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
                    <span>{formatarDataExtenso()}</span>
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
                            <p>Acompanhe suas últimas atividades.</p>
                        </div>

                        <button type="button" className="panel-link">
                            Ver todas
                        </button>
                    </div>

                    <div className="activity-list">
                        {carregando ? (
                            <p className="search-empty">Carregando atividades...</p>
                        ) : atividadesFiltradas.length > 0 ? (
                            atividadesFiltradas.map((atividade) => (
                                <div className="activity-row" key={atividade.id_atividade}>
                                    <div className="activity-symbol">
                                        <ClipboardList size={19} />
                                    </div>

                                    <div className="activity-description">
                                        <strong>{atividade.titulo}</strong>
                                        <small>{atividade.codigo_caso}</small>
                                        <small>{formatarData(atividade.data_prevista)}</small>
                                    </div>

                                    <span className={`activity-status ${classeSituacao(atividade.situacao)}`}>
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
                            <p>Fique atento às datas.</p>
                        </div>

                        <CalendarClock size={20} className="panel-heading-icon" />
                    </div>

                    <div className="deadline-list">
                        {carregando ? (
                            <p className="search-empty">Carregando prazos...</p>
                        ) : prazosFiltrados.length > 0 ? (
                            prazosFiltrados.map((prazo) => {
                                const data = prazo.data_limite
                                    ? new Date(`${prazo.data_limite}T00:00:00`)
                                    : null;

                                return (
                                    <div className="deadline-row" key={prazo.id_prazo}>
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
                                            <small>{formatarData(prazo.data_limite)}</small>
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
            </section>

            {!carregando && !erro && (
                <div className="dashboard-demo-notice">
                    <CheckCircle2 size={20} />
                    <p>
                        <strong>Dados atualizados:</strong> as informações desta
                        visão geral são carregadas a partir dos registros do sistema.
                    </p>
                </div>
            )}
        </>
    );
}
