
import { useOutletContext } from 'react-router-dom';
import {
    ClipboardList,
    FolderOpen,
    CalendarClock,
    Clock3,
    CheckCircle2,
} from 'lucide-react';

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
    // Recebe o termo de pesquisa do cabeçalho principal.
    const outletContext = useOutletContext();
    const searchTerm = outletContext?.searchTerm ?? '';

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
                <CheckCircle2 size={20} />
                <p>
                    <strong>Ambiente demonstrativo:</strong> os indicadores, atividades
                    e prazos apresentados são dados ilustrativos. As informações reais
                    serão carregadas após a integração com o Backend.
                </p>
            </div>
        </>
    );
}
