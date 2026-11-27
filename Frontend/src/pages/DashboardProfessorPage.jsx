
import {
    ClipboardList,
    FolderOpen,
    Users,
    CalendarClock,
    BookOpenCheck,
} from 'lucide-react';

export default function DashboardProfessorPage() {
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

            <section className="indicator-grid">
                <article className="indicator-card">
                    <div className="indicator-icon blue">
                        <FolderOpen size={21} />
                    </div>

                    <div className="indicator-info">
                        <span>Casos jurídicos</span>
                        <strong>Consultar</strong>
                        <small>Casos sob acompanhamento</small>
                    </div>
                </article>

                <article className="indicator-card">
                    <div className="indicator-icon yellow">
                        <Users size={21} />
                    </div>

                    <div className="indicator-info">
                        <span>Alunos</span>
                        <strong>Consultar</strong>
                        <small>Estudantes vinculados</small>
                    </div>
                </article>

                <article className="indicator-card">
                    <div className="indicator-icon orange">
                        <ClipboardList size={21} />
                    </div>

                    <div className="indicator-info">
                        <span>Atividades</span>
                        <strong>Acompanhar</strong>
                        <small>Atividades dos casos</small>
                    </div>
                </article>

                <article className="indicator-card">
                    <div className="indicator-icon green">
                        <CalendarClock size={21} />
                    </div>

                    <div className="indicator-info">
                        <span>Prazos</span>
                        <strong>Verificar</strong>
                        <small>Datas que exigem atenção</small>
                    </div>
                </article>
            </section>

            <section className="dashboard-panels">
                <article className="dashboard-panel">
                    <div className="panel-heading">
                        <div>
                            <h2>Acompanhamento acadêmico</h2>
                            <p>
                                Área destinada ao acompanhamento dos estudantes
                                e das atividades desenvolvidas nos casos.
                            </p>
                        </div>

                        <BookOpenCheck
                            size={22}
                            className="panel-heading-icon"
                        />
                    </div>

                    <p>
                        O Professor/Orientador poderá acompanhar os casos
                        vinculados à sua orientação, verificar atividades
                        e supervisionar o andamento da prática jurídica.
                    </p>
                </article>

                <article className="dashboard-panel">
                    <div className="panel-heading">
                        <div>
                            <h2>Orientações do sistema</h2>
                            <p>Principais responsabilidades do perfil.</p>
                        </div>
                    </div>

                    <ul>
                        <li>Consultar casos jurídicos sob sua orientação.</li>
                        <li>Acompanhar os alunos vinculados aos casos.</li>
                        <li>Verificar atividades e prazos registrados.</li>
                        <li>Supervisionar o andamento dos atendimentos.</li>
                    </ul>
                </article>
            </section>

            <div className="dashboard-demo-notice">
                <BookOpenCheck size={20} />

                <p>
                    <strong>Integração em desenvolvimento:</strong> esta
                    página apresenta a estrutura inicial do painel.
                    Os indicadores e as informações de acompanhamento
                    serão conectados aos dados reais do sistema nas
                    próximas etapas.
                </p>
            </div>
        </div>
    );
}
