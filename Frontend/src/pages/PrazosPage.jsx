
import { useEffect, useMemo, useState } from 'react';
import {
    Search,
    Plus,
    CalendarClock,
    RefreshCw,
    X,
    Pencil,
    CheckCircle2,
    XCircle,
    BriefcaseBusiness,
} from 'lucide-react';

import {
    listarPrazos,
    criarPrazo,
    atualizarPrazo,
} from '../services/prazosService.js';

import { listarCasosJuridicos } from '../services/casosJuridicosService.js';
import { listarAtividades } from '../services/atividadesService.js';
import { apiRequest } from '../services/api.js';
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
        padding: '11px 15px',
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
        padding: '9px 13px',
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

    const partes = String(data).slice(0, 10).split('-');

    if (partes.length === 3) {
        return `${partes[2]}/${partes[1]}/${partes[0]}`;
    }

    return data;
}

function obterCorSituacao(situacao) {
    const cores = {
        'Pendente de validação': {
            background: '#FFF7E6',
            color: '#A15C00',
        },
        'Pendente': {
            background: '#EAF2FB',
            color: '#003874',
        },
        'Concluído': {
            background: '#ECFDF3',
            color: '#16803C',
        },
        'Vencido': {
            background: '#FEE4E2',
            color: '#B42318',
        },
        'Rejeitado': {
            background: '#FEE4E2',
            color: '#B42318',
        },
    };

    return cores[situacao] || {
        background: '#F2F4F7',
        color: '#475467',
    };
}

export default function PrazosPage() {
    const { user } = useAuth();

    const perfil = user?.perfil;

    const [prazos, setPrazos] = useState([]);
    const [casos, setCasos] = useState([]);
    const [atividades, setAtividades] = useState([]);
    const [usuarios, setUsuarios] = useState([]);

    const [searchTerm, setSearchTerm] = useState('');
    const [modalOpen, setModalOpen] = useState(false);
    const [prazoSelecionado, setPrazoSelecionado] = useState(null);
    const [prazoParaRejeitar, setPrazoParaRejeitar] = useState(null);
    const [motivoRejeicao, setMotivoRejeicao] = useState('');

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const [formData, setFormData] = useState({
        id_caso: '',
        id_atividade: '',
        descricao: '',
        data_limite: '',
        id_responsavel: '',
        situacao: 'Pendente',
        observacoes: '',
    });

    const podeCadastrar = ['Gestão', 'Aluno'].includes(perfil);
    const ehGestao = perfil === 'Gestão';
    const ehProfessor = perfil === 'Professor';

    async function carregarDados() {
        setLoading(true);
        setError('');

        try {
            const requisicoes = [
                listarPrazos(),
                listarCasosJuridicos(),
                listarAtividades(),
            ];

            if (ehGestao) {
                requisicoes.push(apiRequest('/usuarios/'));
            }

            const resultados = await Promise.all(requisicoes);

            setPrazos(Array.isArray(resultados[0]) ? resultados[0] : []);
            setCasos(Array.isArray(resultados[1]) ? resultados[1] : []);
            setAtividades(Array.isArray(resultados[2]) ? resultados[2] : []);

            if (ehGestao) {
                const usuariosAtivos = Array.isArray(resultados[3])
                    ? resultados[3].filter(
                        (usuario) =>
                            usuario.situacao_conta === 'Ativo' &&
                            ['Aluno', 'Professor'].includes(usuario.perfil)
                    )
                    : [];

                setUsuarios(usuariosAtivos);
            } else {
                setUsuarios([]);
            }
        } catch (erro) {
            setError(
                erro.message || 'Não foi possível carregar os prazos.'
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

    const usuariosPorId = useMemo(() => {
        return new Map(
            usuarios.map((usuario) => [
                Number(usuario.id_usuario),
                usuario,
            ])
        );
    }, [usuarios]);

    const casosDisponiveis = useMemo(() => {
        return casos.filter(
            (caso) => caso.situacao !== 'Encerrado'
        );
    }, [casos]);

    const atividadesDoCaso = useMemo(() => {
        if (!formData.id_caso) return [];

        return atividades.filter(
            (atividade) =>
                Number(atividade.id_caso) === Number(formData.id_caso)
        );
    }, [atividades, formData.id_caso]);

    const prazosFiltrados = useMemo(() => {
        const termo = searchTerm.toLowerCase().trim();

        if (!termo) return prazos;

        return prazos.filter((prazo) => {
            const caso = casosPorId.get(Number(prazo.id_caso));

            return [
                prazo.descricao,
                prazo.situacao,
                prazo.observacoes,
                prazo.motivo_rejeicao,
                caso?.codigo_interno,
                caso?.titulo_assunto,
            ].some((valor) =>
                String(valor || '').toLowerCase().includes(termo)
            );
        });
    }, [prazos, casosPorId, searchTerm]);

    function abrirModalCadastro() {
        setPrazoSelecionado(null);

        setFormData({
            id_caso: '',
            id_atividade: '',
            descricao: '',
            data_limite: '',
            id_responsavel: '',
            situacao: 'Pendente',
            observacoes: '',
        });

        setError('');
        setSuccess('');
        setModalOpen(true);
    }

    function abrirModalEdicao(prazo) {
        setPrazoSelecionado(prazo);

        setFormData({
            id_caso: String(prazo.id_caso),
            id_atividade: prazo.id_atividade
                ? String(prazo.id_atividade)
                : '',
            descricao: prazo.descricao || '',
            data_limite: prazo.data_limite
                ? String(prazo.data_limite).slice(0, 10)
                : '',
            id_responsavel: String(prazo.id_responsavel || ''),
            situacao: prazo.situacao || 'Pendente',
            observacoes: prazo.observacoes || '',
        });

        setError('');
        setSuccess('');
        setModalOpen(true);
    }

    function fecharModal() {
        if (saving) return;

        setModalOpen(false);
        setPrazoSelecionado(null);
        setError('');
    }

    function handleChange(event) {
        const { name, value } = event.target;

        setFormData((anterior) => ({
            ...anterior,
            [name]: value,
            ...(name === 'id_caso' ? { id_atividade: '' } : {}),
        }));
    }

    async function handleSubmit(event) {
        event.preventDefault();

        setSaving(true);
        setError('');
        setSuccess('');

        try {
            const dados = {
                descricao: formData.descricao.trim(),
                data_limite: formData.data_limite,
                id_atividade: formData.id_atividade
                    ? Number(formData.id_atividade)
                    : null,
                observacoes: formData.observacoes.trim() || null,
            };

            if (ehGestao) {
                dados.id_caso = Number(formData.id_caso);
                dados.id_responsavel = Number(formData.id_responsavel);
                dados.situacao = formData.situacao;
            }

            if (prazoSelecionado) {
                await atualizarPrazo(
                    prazoSelecionado.id_prazo,
                    dados
                );

                setSuccess('Prazo atualizado com sucesso.');
            } else {
                await criarPrazo({
                    ...dados,
                    id_caso: Number(formData.id_caso),
                    ...(ehGestao
                        ? {
                            id_responsavel: Number(formData.id_responsavel),
                            situacao: formData.situacao,
                        }
                        : {}),
                });

                setSuccess('Prazo cadastrado com sucesso.');
            }

            setModalOpen(false);
            setPrazoSelecionado(null);

            await carregarDados();
        } catch (erro) {
            setError(
                erro.message || 'Não foi possível salvar o prazo.'
            );
        } finally {
            setSaving(false);
        }
    }

    async function aprovarPrazo(prazo) {
        const confirmar = window.confirm(
            `Deseja aprovar o prazo "${prazo.descricao}"?`
        );

        if (!confirmar) return;

        setSaving(true);
        setError('');
        setSuccess('');

        try {
            await atualizarPrazo(prazo.id_prazo, {
                situacao: 'Pendente',
            });

            setSuccess('Prazo aprovado com sucesso.');
            await carregarDados();
        } catch (erro) {
            setError(erro.message || 'Não foi possível aprovar o prazo.');
        } finally {
            setSaving(false);
        }
    }

    async function rejeitarPrazo(event) {
        event.preventDefault();

        if (!prazoParaRejeitar) return;

        setSaving(true);
        setError('');

        try {
            await atualizarPrazo(prazoParaRejeitar.id_prazo, {
                situacao: 'Rejeitado',
                motivo_rejeicao: motivoRejeicao.trim(),
            });

            setPrazoParaRejeitar(null);
            setMotivoRejeicao('');
            setSuccess('Prazo rejeitado. A justificativa foi registrada.');

            await carregarDados();
        } catch (erro) {
            setError(erro.message || 'Não foi possível rejeitar o prazo.');
        } finally {
            setSaving(false);
        }
    }

    return (
        <div style={styles.page}>
            <div style={styles.heading}>
                <div>
                    <span style={styles.eyebrow}>GERENCIAMENTO</span>
                    <h1 style={styles.title}>Prazos</h1>
                    <p style={styles.subtitle}>
                        Acompanhe os prazos vinculados aos casos jurídicos.
                    </p>
                </div>

                {podeCadastrar && (
                    <button
                        type="button"
                        style={styles.button}
                        onClick={abrirModalCadastro}
                    >
                        <Plus size={18} />
                        Novo prazo
                    </button>
                )}
            </div>

            <div style={styles.search}>
                <Search size={19} color="#667085" />
                <input
                    type="search"
                    placeholder="Pesquisar por descrição, caso ou situação..."
                    aria-label="Pesquisar prazos"
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

            {error && !modalOpen && !prazoParaRejeitar && (
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

            {success && !modalOpen && !prazoParaRejeitar && (
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
                            Prazos cadastrados
                        </h2>
                        <p
                            style={{
                                color: '#667085',
                                fontSize: '13px',
                                margin: '5px 0 0',
                            }}
                        >
                            {prazosFiltrados.length} prazo(s) encontrado(s)
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
                        Carregando prazos...
                    </div>
                ) : prazosFiltrados.length === 0 ? (
                    <div style={styles.empty}>
                        <CalendarClock
                            size={38}
                            color="#98A2B3"
                            style={{ marginBottom: '12px' }}
                        />

                        <h3 style={{ color: '#344054', fontSize: '16px' }}>
                            Nenhum prazo encontrado
                        </h3>

                        <p style={{ fontSize: '14px' }}>
                            {searchTerm
                                ? 'Tente pesquisar utilizando outros termos.'
                                : 'Ainda não existem prazos disponíveis para exibição.'}
                        </p>
                    </div>
                ) : (
                    prazosFiltrados.map((prazo) => {
                        const caso = casosPorId.get(Number(prazo.id_caso));
                        const corSituacao = obterCorSituacao(prazo.situacao);
                        const responsavel = usuariosPorId.get(
                            Number(prazo.id_responsavel)
                        );

                        const podeValidar =
                            ehProfessor &&
                            prazo.situacao === 'Pendente de validação';

                        return (
                            <div
                                key={prazo.id_prazo}
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
                                            {prazo.descricao}
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
                                                : `Caso #${prazo.id_caso}`}
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
                                            <CalendarClock size={14} />
                                            Data limite: {formatarData(prazo.data_limite)}
                                        </span>

                                        {ehGestao && responsavel && (
                                            <span
                                                style={{
                                                    display: 'block',
                                                    color: '#667085',
                                                    fontSize: '12px',
                                                    marginTop: '5px',
                                                }}
                                            >
                                                Responsável: {responsavel.nome}
                                            </span>
                                        )}

                                        {prazo.motivo_rejeicao && (
                                            <span
                                                style={{
                                                    display: 'block',
                                                    color: '#B42318',
                                                    fontSize: '12px',
                                                    marginTop: '6px',
                                                }}
                                            >
                                                Motivo da rejeição: {prazo.motivo_rejeicao}
                                            </span>
                                        )}
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
                                            background: corSituacao.background,
                                            color: corSituacao.color,
                                            padding: '6px 10px',
                                            borderRadius: '20px',
                                            fontSize: '12px',
                                            fontWeight: '600',
                                        }}
                                    >
                                        {prazo.situacao}
                                    </span>

                                    {ehGestao && (
                                        <button
                                            type="button"
                                            style={styles.secondaryButton}
                                            onClick={() => abrirModalEdicao(prazo)}
                                        >
                                            <Pencil size={15} />
                                            Editar
                                        </button>
                                    )}

                                    {podeValidar && (
                                        <>
                                            <button
                                                type="button"
                                                style={{
                                                    ...styles.secondaryButton,
                                                    color: '#16803C',
                                                }}
                                                onClick={() => aprovarPrazo(prazo)}
                                                disabled={saving}
                                            >
                                                <CheckCircle2 size={15} />
                                                Aprovar
                                            </button>

                                            <button
                                                type="button"
                                                style={{
                                                    ...styles.secondaryButton,
                                                    color: '#B42318',
                                                }}
                                                onClick={() => {
                                                    setPrazoParaRejeitar(prazo);
                                                    setMotivoRejeicao('');
                                                    setError('');
                                                }}
                                                disabled={saving}
                                            >
                                                <XCircle size={15} />
                                                Rejeitar
                                            </button>
                                        </>
                                    )}
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
                        aria-labelledby="prazo-modal-title"
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
                                    id="prazo-modal-title"
                                    style={{
                                        color: '#003874',
                                        fontSize: '21px',
                                        margin: 0,
                                    }}
                                >
                                    {prazoSelecionado ? 'Editar prazo' : 'Novo prazo'}
                                </h2>

                                <p
                                    style={{
                                        color: '#667085',
                                        fontSize: '13px',
                                        margin: '6px 0 0',
                                    }}
                                >
                                    Preencha as informações do prazo.
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
                            <div style={styles.field}>
                                <label style={styles.label}>
                                    Caso jurídico *
                                </label>

                                <select
                                    name="id_caso"
                                    value={formData.id_caso}
                                    onChange={handleChange}
                                    required
                                    disabled={Boolean(prazoSelecionado)}
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
                                        Não há casos disponíveis para cadastrar prazos.
                                    </p>
                                )}
                            </div>

                            <div style={styles.field}>
                                <label style={styles.label}>
                                    Atividade relacionada
                                </label>

                                <select
                                    name="id_atividade"
                                    value={formData.id_atividade}
                                    onChange={handleChange}
                                    style={styles.input}
                                >
                                    <option value="">
                                        Nenhuma atividade específica
                                    </option>

                                    {atividadesDoCaso.map((atividade) => (
                                        <option
                                            key={atividade.id_atividade}
                                            value={atividade.id_atividade}
                                        >
                                            {atividade.titulo}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div style={styles.field}>
                                <label style={styles.label}>
                                    Descrição do prazo *
                                </label>

                                <input
                                    type="text"
                                    name="descricao"
                                    value={formData.descricao}
                                    onChange={handleChange}
                                    maxLength={255}
                                    required
                                    placeholder="Ex.: Entregar documentação complementar"
                                    style={styles.input}
                                />
                            </div>

                            <div style={styles.field}>
                                <label style={styles.label}>
                                    Data limite *
                                </label>

                                <input
                                    type="date"
                                    name="data_limite"
                                    value={formData.data_limite}
                                    onChange={handleChange}
                                    required
                                    style={styles.input}
                                />
                            </div>

                            {ehGestao && (
                                <>
                                    <div style={styles.field}>
                                        <label style={styles.label}>
                                            Responsável *
                                        </label>

                                        <select
                                            name="id_responsavel"
                                            value={formData.id_responsavel}
                                            onChange={handleChange}
                                            required
                                            style={styles.input}
                                        >
                                            <option value="">
                                                Selecione o responsável
                                            </option>

                                            {usuarios.map((usuario) => (
                                                <option
                                                    key={usuario.id_usuario}
                                                    value={usuario.id_usuario}
                                                >
                                                    {usuario.nome} — {usuario.perfil}
                                                </option>
                                            ))}
                                        </select>
                                    </div>

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
                                            <option value="Concluído">Concluído</option>
                                            <option value="Vencido">Vencido</option>
                                        </select>
                                    </div>
                                </>
                            )}

                            <div style={styles.field}>
                                <label style={styles.label}>
                                    Observações
                                </label>

                                <textarea
                                    name="observacoes"
                                    value={formData.observacoes}
                                    onChange={handleChange}
                                    rows={3}
                                    placeholder="Informações adicionais sobre o prazo..."
                                    style={{
                                        ...styles.input,
                                        resize: 'vertical',
                                    }}
                                />
                            </div>

                            {!ehGestao && (
                                <p
                                    style={{
                                        background: '#EAF2FB',
                                        color: '#003874',
                                        padding: '11px 13px',
                                        borderRadius: '7px',
                                        fontSize: '13px',
                                        lineHeight: 1.5,
                                    }}
                                >
                                    Após o cadastro, o prazo ficará pendente de validação
                                    pelo Professor ou pela Gestão. O responsável será
                                    definido automaticamente pelo sistema.
                                </p>
                            )}

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
                                        casosDisponiveis.length === 0 ||
                                        (ehGestao && usuarios.length === 0)
                                    }
                                >
                                    {saving
                                        ? 'Salvando...'
                                        : prazoSelecionado
                                            ? 'Salvar alterações'
                                            : 'Cadastrar prazo'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {prazoParaRejeitar && (
                <div style={styles.modalOverlay}>
                    <div
                        style={styles.modal}
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="rejeitar-prazo-title"
                    >
                        <div
                            style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                gap: '12px',
                                marginBottom: '20px',
                            }}
                        >
                            <div>
                                <h2
                                    id="rejeitar-prazo-title"
                                    style={{
                                        color: '#B42318',
                                        fontSize: '21px',
                                        margin: 0,
                                    }}
                                >
                                    Rejeitar prazo
                                </h2>

                                <p
                                    style={{
                                        color: '#667085',
                                        fontSize: '13px',
                                        margin: '6px 0 0',
                                    }}
                                >
                                    Informe o motivo da rejeição.
                                </p>
                            </div>

                            <button
                                type="button"
                                onClick={() => setPrazoParaRejeitar(null)}
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

                        <form onSubmit={rejeitarPrazo}>
                            <div style={styles.field}>
                                <label style={styles.label}>
                                    Motivo da rejeição *
                                </label>

                                <textarea
                                    value={motivoRejeicao}
                                    onChange={(event) =>
                                        setMotivoRejeicao(event.target.value)
                                    }
                                    required
                                    minLength={1}
                                    rows={4}
                                    placeholder="Explique por que o prazo não foi aprovado..."
                                    style={{
                                        ...styles.input,
                                        resize: 'vertical',
                                    }}
                                />
                            </div>

                            <div
                                style={{
                                    display: 'flex',
                                    justifyContent: 'flex-end',
                                    gap: '10px',
                                    marginTop: '22px',
                                }}
                            >
                                <button
                                    type="button"
                                    style={styles.secondaryButton}
                                    onClick={() => setPrazoParaRejeitar(null)}
                                    disabled={saving}
                                >
                                    Cancelar
                                </button>

                                <button
                                    type="submit"
                                    style={{
                                        ...styles.button,
                                        background: '#B42318',
                                    }}
                                    disabled={saving || !motivoRejeicao.trim()}
                                >
                                    {saving ? 'Enviando...' : 'Confirmar rejeição'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
