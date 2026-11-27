
import { useEffect, useMemo, useState } from 'react';
import {
    Search,
    Plus,
    BriefcaseBusiness,
    CalendarDays,
    RefreshCw,
    X,
    Pencil,
    ClipboardList,
} from 'lucide-react';

import {
    listarAtividades,
    criarAtividade,
    atualizarAtividade,
} from '../services/atividadesService.js';

import { listarCasosJuridicos } from '../services/casosJuridicosService.js';

import { useAuth } from '../contexts/AuthContext.jsx';

const styles = {
    page: {
        padding: '28px',
        color: '#202938',
        fontFamily: 'Inter, Arial, sans-serif',
    },
    heading: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '16px',
        marginBottom: '26px',
    },
    eyebrow: {
        color: '#667085',
        fontSize: '12px',
        fontWeight: '700',
        letterSpacing: '1px',
    },
    title: {
        color: '#003874',
        fontSize: '28px',
        margin: '7px 0',
    },
    subtitle: {
        color: '#667085',
        fontSize: '14px',
        margin: 0,
    },
    button: {
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        background: '#003874',
        color: '#FFFFFF',
        border: 'none',
        borderRadius: '7px',
        padding: '12px 17px',
        fontWeight: '600',
        cursor: 'pointer',
    },
    secondaryButton: {
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        background: '#FFFFFF',
        color: '#003874',
        border: '1px solid #D9DEE8',
        borderRadius: '7px',
        padding: '10px 14px',
        fontWeight: '600',
        cursor: 'pointer',
    },
    search: {
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        background: '#FFFFFF',
        border: '1px solid #D9DEE8',
        borderRadius: '8px',
        padding: '12px 14px',
        maxWidth: '550px',
        width: '100%',
        boxSizing: 'border-box',
    },
    panel: {
        background: '#FFFFFF',
        border: '1px solid #D9DEE8',
        borderRadius: '10px',
        marginTop: '20px',
        overflow: 'hidden',
    },
    panelHeading: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '12px',
        padding: '20px',
        borderBottom: '1px solid #D9DEE8',
    },
    item: {
        padding: '19px 20px',
        borderBottom: '1px solid #EAECF0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '16px',
    },
    icon: {
        background: '#EAF2FB',
        color: '#003874',
        borderRadius: '9px',
        padding: '12px',
        flexShrink: 0,
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
    label: {
        display: 'block',
        fontSize: '13px',
        fontWeight: '600',
        marginBottom: '7px',
        color: '#344054',
    },
    field: {
        marginBottom: '17px',
    },
    empty: {
        textAlign: 'center',
        padding: '45px 20px',
        color: '#667085',
    },
    modalOverlay: {
        position: 'fixed',
        inset: 0,
        background: 'rgba(16, 24, 40, 0.55)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '18px',
        zIndex: 1000,
    },
    modal: {
        background: '#FFFFFF',
        borderRadius: '12px',
        padding: '25px',
        width: '100%',
        maxWidth: '650px',
        maxHeight: '90vh',
        overflowY: 'auto',
        boxSizing: 'border-box',
    },
};

function formatarData(data) {
    if (!data) return 'Não informada';

    const partes = data.slice(0, 10).split('-');

    if (partes.length === 3) {
        return `${partes[2]}/${partes[1]}/${partes[0]}`;
    }

    return data;
}

function obterCorSituacao(situacao) {
    const cores = {
        'Pendente': {
            background: '#FFF7E6',
            color: '#A15C00',
        },
        'Em andamento': {
            background: '#EAF2FB',
            color: '#003874',
        },
        'Concluída': {
            background: '#ECFDF3',
            color: '#16803C',
        },
        'Cancelada': {
            background: '#FEE4E2',
            color: '#B42318',
        },
    };

    return cores[situacao] || {
        background: '#F2F4F7',
        color: '#475467',
    };
}

function obterCorPrioridade(prioridade) {
    const cores = {
        'Baixa': { background: '#ECFDF3', color: '#16803C' },
        'Média': { background: '#FFF7E6', color: '#A15C00' },
        'Alta': { background: '#FEE4E2', color: '#B42318' },
    };

    return cores[prioridade] || {
        background: '#F2F4F7',
        color: '#475467',
    };
}

export default function AtividadesPage() {
    const { user } = useAuth();

    const [atividades, setAtividades] = useState([]);
    const [casos, setCasos] = useState([]);

    const [searchTerm, setSearchTerm] = useState('');
    const [modalOpen, setModalOpen] = useState(false);
    const [atividadeSelecionada, setAtividadeSelecionada] = useState(null);

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const [formData, setFormData] = useState({
        id_caso: '',
        titulo: '',
        descricao: '',
        situacao: 'Pendente',
        prioridade: 'Média',
        data_prevista: '',
    });

    const podeCadastrar = ['Gestão', 'Aluno', 'Professor'].includes(
        user?.perfil
    );

    async function carregarDados() {
        setLoading(true);
        setError('');

        try {
            const [dadosAtividades, dadosCasos] = await Promise.all([
                listarAtividades(),
                listarCasosJuridicos(),
            ]);

            setAtividades(
                Array.isArray(dadosAtividades) ? dadosAtividades : []
            );

            setCasos(
                Array.isArray(dadosCasos) ? dadosCasos : []
            );
        } catch (erro) {
            setError(
                erro.message || 'Não foi possível carregar as atividades.'
            );
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        carregarDados();
    }, []);

    const casosPorId = useMemo(() => {
        return new Map(
            casos.map((caso) => [Number(caso.id_caso), caso])
        );
    }, [casos]);

    const casosDisponiveis = useMemo(() => {
        return casos.filter(
            (caso) => caso.situacao !== 'Encerrado'
        );
    }, [casos]);

    const atividadesFiltradas = useMemo(() => {
        const termo = searchTerm.toLowerCase().trim();

        if (!termo) return atividades;

        return atividades.filter((atividade) => {
            const caso = casosPorId.get(Number(atividade.id_caso));

            const codigoCaso = caso?.codigo_interno || '';
            const tituloCaso = caso?.titulo_assunto || '';

            return [
                atividade.titulo,
                atividade.descricao,
                atividade.situacao,
                atividade.prioridade,
                codigoCaso,
                tituloCaso,
            ].some((valor) =>
                String(valor || '').toLowerCase().includes(termo)
            );
        });
    }, [atividades, casosPorId, searchTerm]);

    function abrirModalCadastro() {
        setAtividadeSelecionada(null);

        setFormData({
            id_caso: '',
            titulo: '',
            descricao: '',
            situacao: 'Pendente',
            prioridade: 'Média',
            data_prevista: '',
        });

        setError('');
        setSuccess('');
        setModalOpen(true);
    }

    function abrirModalEdicao(atividade) {
        setAtividadeSelecionada(atividade);

        setFormData({
            id_caso: String(atividade.id_caso),
            titulo: atividade.titulo || '',
            descricao: atividade.descricao || '',
            situacao: atividade.situacao || 'Pendente',
            prioridade: atividade.prioridade || 'Média',
            data_prevista: atividade.data_prevista
                ? atividade.data_prevista.slice(0, 10)
                : '',
        });

        setError('');
        setSuccess('');
        setModalOpen(true);
    }

    function fecharModal() {
        if (saving) return;

        setModalOpen(false);
        setAtividadeSelecionada(null);
        setError('');
    }

    function handleChange(event) {
        const { name, value } = event.target;

        setFormData((anterior) => ({
            ...anterior,
            [name]: value,
        }));
    }

    async function handleSubmit(event) {
        event.preventDefault();

        setSaving(true);
        setError('');
        setSuccess('');

        try {
            const dados = {
                titulo: formData.titulo.trim(),
                descricao: formData.descricao.trim(),
                situacao: formData.situacao,
                prioridade: formData.prioridade,
                data_prevista: formData.data_prevista || null,
            };

            if (atividadeSelecionada) {
                await atualizarAtividade(
                    atividadeSelecionada.id_atividade,
                    dados
                );

                setSuccess('Atividade atualizada com sucesso.');
            } else {
                await criarAtividade({
                    ...dados,
                    id_caso: Number(formData.id_caso),
                });

                setSuccess('Atividade cadastrada com sucesso.');
            }

            setModalOpen(false);
            setAtividadeSelecionada(null);

            await carregarDados();
        } catch (erro) {
            setError(
                erro.message || 'Não foi possível salvar a atividade.'
            );
        } finally {
            setSaving(false);
        }
    }

    return (
        <div style={styles.page}>
            <div style={styles.heading}>
                <div>
                    <span style={styles.eyebrow}>GERENCIAMENTO</span>
                    <h1 style={styles.title}>Atividades</h1>
                    <p style={styles.subtitle}>
                        Acompanhe e organize as atividades dos casos jurídicos.
                    </p>
                </div>

                {podeCadastrar && (
                    <button
                        type="button"
                        style={styles.button}
                        onClick={abrirModalCadastro}
                    >
                        <Plus size={18} />
                        Nova atividade
                    </button>
                )}
            </div>

            <div style={styles.search}>
                <Search size={19} color="#667085" />
                <input
                    type="search"
                    placeholder="Pesquisar por atividade, caso ou situação..."
                    aria-label="Pesquisar atividades"
                    value={searchTerm}
                    onChange={(event) => setSearchTerm(event.target.value)}
                    style={{
                        border: 'none',
                        outline: 'none',
                        width: '100%',
                        fontSize: '14px',
                        color: '#202938',
                    }}
                />
            </div>

            {error && !modalOpen && (
                <div
                    style={{
                        marginTop: '18px',
                        padding: '13px 16px',
                        background: '#FEE4E2',
                        color: '#B42318',
                        borderRadius: '8px',
                        fontSize: '14px',
                    }}
                >
                    {error}
                </div>
            )}

            {success && !modalOpen && (
                <div
                    style={{
                        marginTop: '18px',
                        padding: '13px 16px',
                        background: '#ECFDF3',
                        color: '#16803C',
                        borderRadius: '8px',
                        fontSize: '14px',
                    }}
                >
                    {success}
                </div>
            )}

            <section style={styles.panel}>
                <div style={styles.panelHeading}>
                    <div>
                        <h2
                            style={{
                                color: '#202938',
                                fontSize: '17px',
                                margin: 0,
                            }}
                        >
                            Atividades cadastradas
                        </h2>
                        <p
                            style={{
                                color: '#667085',
                                fontSize: '13px',
                                margin: '5px 0 0',
                            }}
                        >
                            {atividadesFiltradas.length} atividade(s) encontrada(s)
                        </p>
                    </div>

                    <button
                        type="button"
                        style={styles.secondaryButton}
                        onClick={carregarDados}
                        disabled={loading}
                    >
                        <RefreshCw size={16} />
                        Atualizar
                    </button>
                </div>

                {loading ? (
                    <div style={styles.empty}>
                        Carregando atividades...
                    </div>
                ) : atividadesFiltradas.length === 0 ? (
                    <div style={styles.empty}>
                        <ClipboardList
                            size={38}
                            color="#98A2B3"
                            style={{ marginBottom: '12px' }}
                        />

                        <h3 style={{ color: '#344054', fontSize: '16px' }}>
                            Nenhuma atividade encontrada
                        </h3>

                        <p style={{ fontSize: '14px' }}>
                            {searchTerm
                                ? 'Tente pesquisar utilizando outros termos.'
                                : 'Ainda não existem atividades disponíveis para exibição.'}
                        </p>
                    </div>
                ) : (
                    atividadesFiltradas.map((atividade) => {
                        const caso = casosPorId.get(
                            Number(atividade.id_caso)
                        );

                        const corSituacao = obterCorSituacao(
                            atividade.situacao
                        );

                        const corPrioridade = obterCorPrioridade(
                            atividade.prioridade
                        );

                        return (
                            <div
                                key={atividade.id_atividade}
                                style={styles.item}
                            >
                                <div
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '15px',
                                        flex: 1,
                                        minWidth: '220px',
                                    }}
                                >
                                    <div style={styles.icon}>
                                        <BriefcaseBusiness size={22} />
                                    </div>

                                    <div style={{ minWidth: 0 }}>
                                        <strong
                                            style={{
                                                display: 'block',
                                                color: '#202938',
                                                fontSize: '15px',
                                                marginBottom: '6px',
                                            }}
                                        >
                                            {atividade.titulo}
                                        </strong>

                                        <span
                                            style={{
                                                display: 'block',
                                                color: '#667085',
                                                fontSize: '13px',
                                                marginBottom: '5px',
                                            }}
                                        >
                                            {caso
                                                ? `${caso.codigo_interno} — ${caso.titulo_assunto}`
                                                : `Caso #${atividade.id_caso}`}
                                        </span>

                                        <span
                                            style={{
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '5px',
                                                color: '#667085',
                                                fontSize: '12px',
                                            }}
                                        >
                                            <CalendarDays size={14} />
                                            Prazo: {formatarData(atividade.data_prevista)}
                                        </span>
                                    </div>
                                </div>

                                <div
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        flexWrap: 'wrap',
                                        gap: '9px',
                                    }}
                                >
                                    <span
                                        style={{
                                            background: corPrioridade.background,
                                            color: corPrioridade.color,
                                            padding: '6px 10px',
                                            borderRadius: '20px',
                                            fontSize: '12px',
                                            fontWeight: '600',
                                        }}
                                    >
                                        {atividade.prioridade}
                                    </span>

                                    <span
                                        style={{
                                            background: corSituacao.background,
                                            color: corSituacao.color,
                                            padding: '6px 10px',
                                            borderRadius: '20px',
                                            fontSize: '12px',
                                            fontWeight: '600',
                                        }}
                                    >
                                        {atividade.situacao}
                                    </span>

                                    <button
                                        type="button"
                                        style={styles.secondaryButton}
                                        onClick={() => abrirModalEdicao(atividade)}
                                    >
                                        <Pencil size={15} />
                                        Editar
                                    </button>
                                </div>
                            </div>
                        );
                    })
                )}
            </section>

            {modalOpen && (
                <div style={styles.modalOverlay}>
                    <div
                        style={styles.modal}
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="atividade-modal-title"
                    >
                        <div
                            style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                gap: '12px',
                                marginBottom: '22px',
                            }}
                        >
                            <div>
                                <h2
                                    id="atividade-modal-title"
                                    style={{
                                        color: '#003874',
                                        fontSize: '21px',
                                        margin: 0,
                                    }}
                                >
                                    {atividadeSelecionada
                                        ? 'Editar atividade'
                                        : 'Nova atividade'}
                                </h2>

                                <p
                                    style={{
                                        color: '#667085',
                                        fontSize: '13px',
                                        margin: '6px 0 0',
                                    }}
                                >
                                    Preencha as informações da atividade.
                                </p>
                            </div>

                            <button
                                type="button"
                                onClick={fecharModal}
                                disabled={saving}
                                aria-label="Fechar"
                                style={{
                                    border: 'none',
                                    background: 'transparent',
                                    cursor: 'pointer',
                                    color: '#667085',
                                }}
                            >
                                <X size={22} />
                            </button>
                        </div>

                        {error && (
                            <div
                                style={{
                                    background: '#FEE4E2',
                                    color: '#B42318',
                                    padding: '12px',
                                    borderRadius: '7px',
                                    marginBottom: '16px',
                                    fontSize: '13px',
                                }}
                            >
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit}>
                            {!atividadeSelecionada && (
                                <div style={styles.field}>
                                    <label style={styles.label}>
                                        Caso jurídico *
                                    </label>

                                    <select
                                        name="id_caso"
                                        value={formData.id_caso}
                                        onChange={handleChange}
                                        required
                                        style={styles.input}
                                    >
                                        <option value="">
                                            Selecione o caso jurídico
                                        </option>

                                        {casosDisponiveis.map((caso) => (
                                            <option
                                                key={caso.id_caso}
                                                value={caso.id_caso}
                                            >
                                                {caso.codigo_interno} — {caso.titulo_assunto}
                                            </option>
                                        ))}
                                    </select>

                                    {casosDisponiveis.length === 0 && (
                                        <p
                                            style={{
                                                color: '#A15C00',
                                                fontSize: '12px',
                                                marginTop: '7px',
                                            }}
                                        >
                                            Não há casos disponíveis para cadastrar atividades.
                                        </p>
                                    )}
                                </div>
                            )}

                            <div style={styles.field}>
                                <label style={styles.label}>
                                    Título *
                                </label>

                                <input
                                    type="text"
                                    name="titulo"
                                    value={formData.titulo}
                                    onChange={handleChange}
                                    maxLength={150}
                                    required
                                    placeholder="Ex.: Analisar documentação do assistido"
                                    style={styles.input}
                                />
                            </div>

                            <div style={styles.field}>
                                <label style={styles.label}>
                                    Descrição *
                                </label>

                                <textarea
                                    name="descricao"
                                    value={formData.descricao}
                                    onChange={handleChange}
                                    required
                                    rows={4}
                                    placeholder="Descreva o que precisa ser realizado..."
                                    style={{
                                        ...styles.input,
                                        resize: 'vertical',
                                    }}
                                />
                            </div>

                            <div
                                style={{
                                    display: 'grid',
                                    gridTemplateColumns: '1fr 1fr',
                                    gap: '14px',
                                }}
                            >
                                <div style={styles.field}>
                                    <label style={styles.label}>
                                        Situação
                                    </label>

                                    <select
                                        name="situacao"
                                        value={formData.situacao}
                                        onChange={handleChange}
                                        style={styles.input}
                                    >
                                        <option value="Pendente">Pendente</option>
                                        <option value="Em andamento">Em andamento</option>
                                        <option value="Concluída">Concluída</option>
                                        <option value="Cancelada">Cancelada</option>
                                    </select>
                                </div>

                                <div style={styles.field}>
                                    <label style={styles.label}>
                                        Prioridade
                                    </label>

                                    <select
                                        name="prioridade"
                                        value={formData.prioridade}
                                        onChange={handleChange}
                                        style={styles.input}
                                    >
                                        <option value="Baixa">Baixa</option>
                                        <option value="Média">Média</option>
                                        <option value="Alta">Alta</option>
                                    </select>
                                </div>
                            </div>

                            <div style={styles.field}>
                                <label style={styles.label}>
                                    Data prevista
                                </label>

                                <input
                                    type="date"
                                    name="data_prevista"
                                    value={formData.data_prevista}
                                    onChange={handleChange}
                                    style={styles.input}
                                />
                            </div>

                            <div
                                style={{
                                    display: 'flex',
                                    justifyContent: 'flex-end',
                                    gap: '10px',
                                    marginTop: '25px',
                                    flexWrap: 'wrap',
                                }}
                            >
                                <button
                                    type="button"
                                    style={styles.secondaryButton}
                                    onClick={fecharModal}
                                    disabled={saving}
                                >
                                    Cancelar
                                </button>

                                <button
                                    type="submit"
                                    style={styles.button}
                                    disabled={
                                        saving ||
                                        (!atividadeSelecionada &&
                                            casosDisponiveis.length === 0)
                                    }
                                >
                                    {saving
                                        ? 'Salvando...'
                                        : atividadeSelecionada
                                            ? 'Salvar alterações'
                                            : 'Cadastrar atividade'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
