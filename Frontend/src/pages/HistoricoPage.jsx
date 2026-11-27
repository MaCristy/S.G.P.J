
import { useEffect, useMemo, useState } from 'react';
import {
    History,
    Search,
    RefreshCw,
    CalendarClock,
    BriefcaseBusiness,
    UserRound,
    FileText,
} from 'lucide-react';

import {
    listarHistorico,
    listarHistoricoPorCaso,
} from '../services/historicoService.js';

import { listarCasosJuridicos } from '../services/casosJuridicosService.js';

const styles = {
    page: {
        padding: '28px',
        color: '#202938',
        fontFamily: 'Inter, Arial, sans-serif',
    },
    heading: {
        marginBottom: '26px',
    },
    eyebrow: {
        color: '#667085',
        fontSize: '12px',
        fontWeight: '700',
        letterSpacing: '1px',
    },
    title: {
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        color: '#003874',
        fontSize: '28px',
        margin: '7px 0',
    },
    subtitle: {
        color: '#667085',
        fontSize: '14px',
        margin: 0,
    },
    filters: {
        display: 'flex',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '12px',
        marginBottom: '20px',
    },
    input: {
        width: '100%',
        padding: '11px 12px',
        border: '1px solid #D9DEE8',
        borderRadius: '7px',
        fontSize: '14px',
        boxSizing: 'border-box',
        background: '#FFFFFF',
        color: '#202938',
    },
    search: {
        display: 'flex',
        alignItems: 'center',
        gap: '9px',
        background: '#FFFFFF',
        border: '1px solid #D9DEE8',
        borderRadius: '7px',
        padding: '0 12px',
        flex: '1',
        minWidth: '220px',
    },
    searchInput: {
        border: 'none',
        outline: 'none',
        padding: '12px 0',
        width: '100%',
        fontSize: '14px',
        background: 'transparent',
        color: '#202938',
    },
    select: {
        ...{
            width: '100%',
            padding: '11px 12px',
            border: '1px solid #D9DEE8',
            borderRadius: '7px',
            fontSize: '14px',
            boxSizing: 'border-box',
            background: '#FFFFFF',
            color: '#202938',
        },
        maxWidth: '320px',
    },
    button: {
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        background: '#FFFFFF',
        color: '#003874',
        border: '1px solid #D9DEE8',
        borderRadius: '7px',
        padding: '10px 13px',
        fontWeight: '600',
        cursor: 'pointer',
    },
    panel: {
        background: '#FFFFFF',
        border: '1px solid #D9DEE8',
        borderRadius: '10px',
        overflow: 'hidden',
    },
    panelHeading: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '10px',
        padding: '19px 20px',
        borderBottom: '1px solid #D9DEE8',
    },
    timeline: {
        padding: '8px 22px',
    },
    item: {
        display: 'flex',
        gap: '15px',
        padding: '20px 0',
        borderBottom: '1px solid #EAECF0',
    },
    iconArea: {
        width: '42px',
        height: '42px',
        minWidth: '42px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#EAF2FB',
        color: '#003874',
        borderRadius: '10px',
    },
    itemTitle: {
        color: '#202938',
        fontSize: '15px',
        fontWeight: '700',
        margin: '0 0 7px',
    },
    description: {
        color: '#475467',
        fontSize: '14px',
        lineHeight: '1.6',
        margin: '0 0 12px',
        whiteSpace: 'pre-wrap',
    },
    metadata: {
        display: 'flex',
        flexWrap: 'wrap',
        gap: '15px',
        color: '#667085',
        fontSize: '12px',
    },
    empty: {
        textAlign: 'center',
        padding: '50px 20px',
        color: '#667085',
    },
    message: {
        padding: '15px',
        borderRadius: '8px',
        fontSize: '13px',
        marginBottom: '16px',
    },
};

function formatarDataHora(data) {
    if (!data) return 'Data não informada';

    const dataConvertida = new Date(data);

    if (Number.isNaN(dataConvertida.getTime())) {
        return 'Data não disponível';
    }

    return dataConvertida.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}

export default function HistoricoPage() {
    const [historicos, setHistoricos] = useState([]);
    const [casos, setCasos] = useState([]);

    const [casoSelecionado, setCasoSelecionado] = useState('');
    const [pesquisa, setPesquisa] = useState('');

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    async function carregarDados() {
        try {
            setLoading(true);
            setError('');

            const [historicoResponse, casosResponse] = await Promise.all([
                casoSelecionado
                    ? listarHistoricoPorCaso(casoSelecionado)
                    : listarHistorico(),
                listarCasosJuridicos(),
            ]);

            setHistoricos(Array.isArray(historicoResponse) ? historicoResponse : []);
            setCasos(Array.isArray(casosResponse) ? casosResponse : []);
        } catch (erro) {
            setError(erro.message || 'Não foi possível carregar o histórico.');
            setHistoricos([]);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        carregarDados();
    }, [casoSelecionado]);

    const historicosFiltrados = useMemo(() => {
        const termo = pesquisa.trim().toLowerCase();

        return [...historicos]
            .filter((item) => {
                if (!termo) return true;

                const caso = casos.find(
                    (registro) => registro.id_caso === item.id_caso
                );

                const texto = [
                    item.tipo_ocorrencia,
                    item.descricao,
                    item.id_usuario_responsavel,
                    item.referencia_registro_afetado,
                    caso?.codigo_interno,
                    caso?.titulo_assunto,
                ]
                    .filter(Boolean)
                    .join(' ')
                    .toLowerCase();

                return texto.includes(termo);
            })
            .sort(
                (a, b) =>
                    new Date(b.data_hora).getTime() -
                    new Date(a.data_hora).getTime()
            );
    }, [historicos, pesquisa, casos]);

    function obterIdentificacaoCaso(idCaso) {
        const caso = casos.find(
            (item) => item.id_caso === idCaso
        );

        if (!caso) {
            return `Caso #${idCaso}`;
        }

        return `${caso.codigo_interno} — ${caso.titulo_assunto}`;
    }

    return (
        <div style={styles.page}>
            <header style={styles.heading}>
                <span style={styles.eyebrow}>
                    ACOMPANHAMENTO
                </span>

                <h1 style={styles.title}>
                    <History size={27} />
                    Histórico
                </h1>

                <p style={styles.subtitle}>
                    Consulte as ocorrências e alterações registradas
                    nos casos jurídicos.
                </p>
            </header>

            {error && (
                <div
                    style={{
                        ...styles.message,
                        background: '#FEE4E2',
                        color: '#B42318',
                    }}
                >
                    {error}
                </div>
            )}

            <div style={styles.filters}>
                <div style={styles.search}>
                    <Search size={18} color="#667085" />

                    <input
                        type="text"
                        value={pesquisa}
                        onChange={(e) => setPesquisa(e.target.value)}
                        placeholder="Pesquisar ocorrência, descrição ou caso..."
                        style={styles.searchInput}
                    />
                </div>

                <select
                    value={casoSelecionado}
                    onChange={(e) => setCasoSelecionado(e.target.value)}
                    style={styles.select}
                >
                    <option value="">Todos os casos disponíveis</option>

                    {casos.map((caso) => (
                        <option
                            key={caso.id_caso}
                            value={caso.id_caso}
                        >
                            {caso.codigo_interno} — {caso.titulo_assunto}
                        </option>
                    ))}
                </select>

                <button
                    type="button"
                    onClick={carregarDados}
                    style={styles.button}
                    disabled={loading}
                >
                    <RefreshCw size={16} />
                    Atualizar
                </button>
            </div>

            <section style={styles.panel}>
                <div style={styles.panelHeading}>
                    <div>
                        <strong style={{ color: '#003874' }}>
                            Linha do tempo
                        </strong>

                        <p
                            style={{
                                color: '#667085',
                                fontSize: '12px',
                                margin: '5px 0 0',
                            }}
                        >
                            {historicosFiltrados.length} ocorrência(s) encontrada(s)
                        </p>
                    </div>
                </div>

                {loading ? (
                    <div style={styles.empty}>
                        Carregando histórico...
                    </div>
                ) : historicosFiltrados.length === 0 ? (
                    <div style={styles.empty}>
                        <History
                            size={38}
                            color="#98A2B3"
                            style={{ marginBottom: '12px' }}
                        />

                        <p style={{ fontWeight: '600', margin: '0 0 7px' }}>
                            Nenhuma ocorrência encontrada
                        </p>

                        <p style={{ fontSize: '13px', margin: 0 }}>
                            Não há registros históricos para os filtros selecionados.
                        </p>
                    </div>
                ) : (
                    <div style={styles.timeline}>
                        {historicosFiltrados.map((item) => (
                            <article
                                key={item.id_historico}
                                style={styles.item}
                            >
                                <div style={styles.iconArea}>
                                    <FileText size={20} />
                                </div>

                                <div style={{ flex: 1, minWidth: 0 }}>
                                    <h3 style={styles.itemTitle}>
                                        {item.tipo_ocorrencia}
                                    </h3>

                                    <p style={styles.description}>
                                        {item.descricao}
                                    </p>

                                    <div style={styles.metadata}>
                                        <span
                                            style={{
                                                display: 'inline-flex',
                                                alignItems: 'center',
                                                gap: '5px',
                                            }}
                                        >
                                            <BriefcaseBusiness size={14} />
                                            {obterIdentificacaoCaso(item.id_caso)}
                                        </span>

                                        <span
                                            style={{
                                                display: 'inline-flex',
                                                alignItems: 'center',
                                                gap: '5px',
                                            }}
                                        >
                                            <UserRound size={14} />
                                            Usuário #{item.id_usuario_responsavel}
                                        </span>

                                        <span
                                            style={{
                                                display: 'inline-flex',
                                                alignItems: 'center',
                                                gap: '5px',
                                            }}
                                        >
                                            <CalendarClock size={14} />
                                            {formatarDataHora(item.data_hora)}
                                        </span>
                                    </div>

                                    {item.referencia_registro_afetado && (
                                        <p
                                            style={{
                                                color: '#667085',
                                                fontSize: '12px',
                                                margin: '10px 0 0',
                                            }}
                                        >
                                            Registro relacionado:{' '}
                                            {item.referencia_registro_afetado}
                                        </p>
                                    )}
                                </div>
                            </article>
                        ))}
                    </div>
                )}
            </section>
        </div>
    );
}
