
import { useEffect, useState } from 'react';
import {
    Search,
    Plus,
    BriefcaseBusiness,
    CalendarDays,
    UserRound,
    RefreshCw,
    X,
    Eye,
} from 'lucide-react';

import {
    listarCasosJuridicos,
    criarCasoJuridico,
    atualizarCasoJuridico,
} from '../services/casosJuridicosService.js';

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
        padding: '12px 17px',
        fontWeight: '600',
        cursor: 'pointer',
    },
    secondaryButton: {
        display: 'inline-flex',
        alignItems: 'center',
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

function obterDataAtual() {
    const agora = new Date();
    const deslocamento = agora.getTimezoneOffset() * 60000;

    return new Date(agora.getTime() - deslocamento)
        .toISOString()
        .slice(0, 10);
}

function formatarData(data) {
    if (!data) return 'Não informada';

    const partes = data.split('-');

    if (partes.length === 3) {
        return `${partes[2]}/${partes[1]}/${partes[0]}`;
    }

    return data;
}

function obterCorSituacao(situacao) {
    const cores = {
        'Em triagem': {
            background: '#FFF7E6',
            color: '#A15C00',
        },
        'Aberto': {
            background: '#EAF2FB',
            color: '#003874',
        },
        'Em Andamento': {
            background: '#ECFDF3',
            color: '#16803C',
        },
        'Suspenso': {
            background: '#F2F4F7',
            color: '#475467',
        },
        'Encerrado': {
            background: '#FEE4E2',
            color: '#B42318',
        },
    };

    return cores[situacao] || {
        background: '#F2F4F7',
        color: '#475467',
    };
}

export default function CasosJuridicosPage() {
    const { user } = useAuth();

    const perfil = user?.perfil;
    const podeCadastrar = perfil === 'Gestão' || perfil === 'Aluno';

    const [casos, setCasos] = useState([]);
    const [assistidos, setAssistidos] = useState([]);

    const [professores, setProfessores] = useState([]);
    const [associacaoOpen, setAssociacaoOpen] = useState(false);
    const [casoParaAssociar, setCasoParaAssociar] = useState(null);
    const [professorSelecionado, setProfessorSelecionado] = useState('');
    const [associationError, setAssociationError] = useState('');

    const [searchTerm, setSearchTerm] = useState('');
    const [modalOpen, setModalOpen] = useState(false);
    const [casoSelecionado, setCasoSelecionado] = useState(null);

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [validationError, setValidationError] = useState('');

    const [formData, setFormData] = useState({
        codigo_interno: '',
        id_assistido: '',
        titulo_assunto: '',
        descricao: '',
        area_juridica: '',
        data_abertura: obterDataAtual(),
        id_professor_orientador: '',
    });

    async function carregarDados() {
        setLoading(true);
        setError('');

        try {
            const [dadosCasos, dadosAssistidos, dadosProfessores] = await Promise.all([
                listarCasosJuridicos(),
                apiRequest('/assistidos/'),
                ['Gestão', 'Aluno'].includes(perfil)
                    ? apiRequest('/professores/')
                    : Promise.resolve([]),
            ]);

            setCasos(Array.isArray(dadosCasos) ? dadosCasos : []);

            setAssistidos(
                Array.isArray(dadosAssistidos) ? dadosAssistidos : []
            );

            setProfessores(
                Array.isArray(dadosProfessores)
                    ? dadosProfessores.filter(
                        (professor) => professor.situacao === 'Ativo'
                    )
                    : []
            );
        } catch (erro) {
            setError(
                erro.message || 'Não foi possível carregar os casos jurídicos.'
            );
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        carregarDados();
    }, []);

    function handleChange(event) {
        const { name, value } = event.target;

        setFormData((anterior) => ({
            ...anterior,
            [name]: value,
        }));
    }

    function abrirFormulario() {
        setFormData({
            codigo_interno: '',
            id_assistido: '',
            titulo_assunto: '',
            descricao: '',
            area_juridica: '',
            data_abertura: obterDataAtual(),
        });

        setError('');
        setSuccess('');
        setModalOpen(true);
    }

    function fecharFormulario() {
        if (saving) return;

        setModalOpen(false);
        setError('');
    }

    function abrirAssociacaoProfessor(caso) {
        setCasoParaAssociar(caso);
        setProfessorSelecionado(
            caso.id_professor_orientador
                ? String(caso.id_professor_orientador)
                : ''
        );
        setAssociationError('');
        setAssociacaoOpen(true);
    }

    async function salvarAssociacaoProfessor() {
        if (!professorSelecionado) {
            setAssociationError('Selecione um professor orientador.');
            return;
        }

        try {
            setSaving(true);
            setAssociationError('');

            await atualizarCasoJuridico(casoParaAssociar.id_caso, {
                id_professor_orientador: Number(professorSelecionado),
            });

            setAssociacaoOpen(false);
            setCasoParaAssociar(null);
            setProfessorSelecionado('');

            await carregarDados();
        } catch (err) {
            setAssociationError(
                err.message || 'Não foi possível associar o professor.'
            );
        } finally {
            setSaving(false);
        }
    }

    async function validarCaso() {
        if (!casoSelecionado) return;

        try {
            setSaving(true);
            setValidationError('');

            await atualizarCasoJuridico(casoSelecionado.id_caso, {
                situacao: 'Aberto',
            });

            setCasoSelecionado((anterior) => ({
                ...anterior,
                situacao: 'Aberto',
            }));

            setSuccess('Caso jurídico validado com sucesso!');

            await carregarDados();
        } catch (erro) {
            setValidationError(
                erro.message || 'Não foi possível validar o caso jurídico.'
            );
        } finally {
            setSaving(false);
        }
    }

    async function handleSubmit(event) {
        event.preventDefault();

        setSaving(true);
        setError('');
        setSuccess('');

        const dados = {
            codigo_interno: formData.codigo_interno.trim(),
            id_assistido: Number(formData.id_assistido),
            titulo_assunto: formData.titulo_assunto.trim(),
            descricao: formData.descricao.trim(),
            area_juridica: formData.area_juridica.trim(),
            data_abertura: formData.data_abertura,
            id_professor_orientador: Number(formData.id_professor_orientador),
        };

        try {
            await criarCasoJuridico(dados);

            setModalOpen(false);
            setSuccess('Caso jurídico cadastrado com sucesso!');

            await carregarDados();
        } catch (erro) {
            setError(
                erro.message || 'Não foi possível cadastrar o caso jurídico.'
            );
        } finally {
            setSaving(false);
        }
    }

    function obterNomeAssistido(idAssistido) {
        const assistido = assistidos.find(
            (item) => item.id_assistido === idAssistido
        );

        return assistido?.nome_completo || `Assistido #${idAssistido}`;
    }

    const casosFiltrados = casos.filter((caso) => {
        const nomeAssistido = obterNomeAssistido(caso.id_assistido);

        const texto = [
            caso.codigo_interno,
            caso.titulo_assunto,
            caso.area_juridica,
            caso.situacao,
            nomeAssistido,
        ]
            .filter(Boolean)
            .join(' ')
            .toLowerCase();

        return texto.includes(searchTerm.toLowerCase());
    });

    const assistidosAtivos = assistidos.filter(
        (assistido) => assistido.situacao === 'Ativo'
    );

    return (
        <main style={styles.page}>
            <header style={styles.heading}>
                <div>
                    <span style={styles.eyebrow}>
                        GESTÃO DA PRÁTICA JURÍDICA
                    </span>

                    <h1 style={styles.title}>Casos Jurídicos</h1>

                    <p style={styles.subtitle}>
                        Gerencie e acompanhe os casos vinculados aos assistidos.
                    </p>
                </div>

                {podeCadastrar && (
                    <button
                        type="button"
                        style={styles.button}
                        onClick={abrirFormulario}
                    >
                        <Plus size={18} />
                        Novo caso jurídico
                    </button>
                )}
            </header>

            <section style={styles.search}>
                <Search size={19} color="#667085" />

                <input
                    type="search"
                    aria-label="Pesquisar casos jurídicos"
                    placeholder="Pesquisar por código, título, assistido ou área..."
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
            </section>

            {success && (
                <p
                    role="status"
                    style={{
                        color: '#16803C',
                        background: '#ECFDF3',
                        padding: '12px',
                        borderRadius: '7px',
                        marginTop: '16px',
                    }}
                >
                    {success}
                </p>
            )}

            {error && (
                <div
                    role="alert"
                    style={{
                        color: '#B42318',
                        background: '#FEF3F2',
                        padding: '13px',
                        borderRadius: '7px',
                        marginTop: '16px',
                    }}
                >
                    {error}
                </div>
            )}

            <section style={styles.panel}>
                <div style={styles.panelHeading}>
                    <div>
                        <h2 style={{ fontSize: '17px', margin: '0 0 5px' }}>
                            Relação de casos
                        </h2>

                        <p style={{
                            color: '#667085',
                            fontSize: '13px',
                            margin: 0,
                        }}>
                            Casos disponíveis conforme seu perfil de acesso.
                        </p>
                    </div>

                    <button
                        type="button"
                        onClick={carregarDados}
                        title="Atualizar lista"
                        aria-label="Atualizar lista"
                        style={styles.secondaryButton}
                    >
                        <RefreshCw size={16} />
                        Atualizar
                    </button>
                </div>

                {loading ? (
                    <div style={styles.empty}>
                        Carregando casos jurídicos...
                    </div>
                ) : casosFiltrados.length === 0 ? (
                    <div style={styles.empty}>
                        <BriefcaseBusiness
                            size={38}
                            color="#98A2B3"
                            style={{ marginBottom: '12px' }}
                        />

                        <p style={{ fontWeight: '600', margin: '0 0 6px' }}>
                            Nenhum caso jurídico encontrado.
                        </p>

                        <p style={{ fontSize: '13px', margin: 0 }}>
                            Os casos disponíveis para seu perfil aparecerão aqui.
                        </p>
                    </div>
                ) : (
                    casosFiltrados.map((caso) => {
                        const cor = obterCorSituacao(caso.situacao);

                        return (
                            <article
                                key={caso.id_caso}
                                style={styles.item}
                            >
                                <div style={{
                                    display: 'flex',
                                    alignItems: 'flex-start',
                                    gap: '14px',
                                    flex: 1,
                                    minWidth: '230px',
                                }}>
                                    <div style={styles.icon}>
                                        <BriefcaseBusiness size={21} />
                                    </div>

                                    <div>
                                        <h3 style={{
                                            color: '#202938',
                                            fontSize: '15px',
                                            margin: '0 0 6px',
                                        }}>
                                            {caso.titulo_assunto}
                                        </h3>

                                        <p style={{
                                            color: '#667085',
                                            fontSize: '13px',
                                            margin: '0 0 7px',
                                        }}>
                                            Código: {caso.codigo_interno}
                                        </p>

                                        <p style={{
                                            color: '#667085',
                                            fontSize: '13px',
                                            margin: '0 0 7px',
                                        }}>
                                            <UserRound
                                                size={14}
                                                style={{
                                                    verticalAlign: 'middle',
                                                    marginRight: '5px',
                                                }}
                                            />
                                            {obterNomeAssistido(caso.id_assistido)}
                                        </p>

                                        <p style={{
                                            color: '#667085',
                                            fontSize: '13px',
                                            margin: 0,
                                        }}>
                                            <CalendarDays
                                                size={14}
                                                style={{
                                                    verticalAlign: 'middle',
                                                    marginRight: '5px',
                                                }}
                                            />
                                            Abertura: {formatarData(caso.data_abertura)}
                                        </p>
                                    </div>
                                </div>

                                <div style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '12px',
                                    flexWrap: 'wrap',
                                }}>
                                    <span style={{
                                        background: cor.background,
                                        color: cor.color,
                                        padding: '6px 11px',
                                        borderRadius: '20px',
                                        fontSize: '12px',
                                        fontWeight: '700',
                                    }}>
                                        {caso.situacao}
                                    </span>

                                    <button
                                        type="button"
                                        onClick={() => setCasoSelecionado(caso)}
                                        title="Visualizar detalhes"
                                        aria-label="Visualizar detalhes"
                                        style={{
                                            ...styles.secondaryButton,
                                            padding: '9px 12px',
                                        }}
                                    >
                                        <Eye size={16} />
                                        Detalhes
                                    </button>
                                    {perfil === 'Gestão' && (
                                        <button
                                            type="button"
                                            onClick={() => abrirAssociacaoProfessor(caso)}
                                            style={{
                                                ...styles.secondaryButton,
                                                padding: '9px 12px',
                                            }}
                                        >
                                            {caso.id_professor_orientador
                                                ? 'Alterar professor'
                                                : 'Associar professor'}
                                        </button>
                                    )}
                                </div>
                            </article>
                        );
                    })
                )}
            </section>

            {modalOpen && (
                <div style={styles.modalOverlay}>
                    <section
                        style={styles.modal}
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="titulo-modal-caso"
                    >
                        <header style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            marginBottom: '22px',
                        }}>
                            <div>
                                <h2
                                    id="titulo-modal-caso"
                                    style={{
                                        color: '#003874',
                                        margin: '0 0 6px',
                                        fontSize: '20px',
                                    }}
                                >
                                    Novo caso jurídico
                                </h2>

                                <p style={{
                                    color: '#667085',
                                    fontSize: '13px',
                                    margin: 0,
                                }}>
                                    Preencha os dados para registrar o caso.
                                </p>
                            </div>

                            <button
                                type="button"
                                onClick={fecharFormulario}
                                disabled={saving}
                                aria-label="Fechar formulário"
                                style={{
                                    border: 'none',
                                    background: 'transparent',
                                    cursor: 'pointer',
                                    color: '#667085',
                                }}
                            >
                                <X size={21} />
                            </button>
                        </header>

                        <form onSubmit={handleSubmit}>
                            <div style={styles.field}>
                                <label style={styles.label}>
                                    Código interno *
                                </label>

                                <input
                                    name="codigo_interno"
                                    value={formData.codigo_interno}
                                    onChange={handleChange}
                                    style={styles.input}
                                    placeholder="Ex.: CASO-2026-001"
                                    required
                                    maxLength={50}
                                />
                            </div>

                            <div style={styles.field}>
                                <label style={styles.label}>
                                    Assistido *
                                </label>

                                <select
                                    name="id_assistido"
                                    value={formData.id_assistido}
                                    onChange={handleChange}
                                    style={styles.input}
                                    required
                                >
                                    <option value="">
                                        Selecione o assistido
                                    </option>

                                    {assistidosAtivos.map((assistido) => (
                                        <option
                                            key={assistido.id_assistido}
                                            value={assistido.id_assistido}
                                        >
                                            {assistido.nome_completo}
                                        </option>
                                    ))}
                                </select>

                                {assistidosAtivos.length === 0 && (
                                    <p style={{
                                        color: '#B42318',
                                        fontSize: '12px',
                                    }}>
                                        Não há assistidos ativos disponíveis.
                                    </p>
                                )}
                            </div>

                            {professores.length > 0 && (
                                <div style={styles.field}>
                                    <label style={styles.label}>
                                        Professor orientador *
                                    </label>

                                    <select
                                        name="id_professor_orientador"
                                        value={formData.id_professor_orientador}
                                        onChange={handleChange}
                                        style={styles.input}
                                        required
                                    >
                                        <option value="">
                                            Selecione o professor orientador
                                        </option>

                                        {professores.map((professor) => (
                                            <option
                                                key={professor.id_professor}
                                                value={professor.id_professor}
                                            >
                                                {professor.identificacao_funcional}
                                                {professor.area_vinculo
                                                    ? ` — ${professor.area_vinculo}`
                                                    : ''}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            )}

                            <div style={styles.field}>
                                <label style={styles.label}>
                                    Título / assunto *
                                </label>

                                <input
                                    name="titulo_assunto"
                                    value={formData.titulo_assunto}
                                    onChange={handleChange}
                                    style={styles.input}
                                    placeholder="Informe o assunto do caso"
                                    required
                                    maxLength={200}
                                />
                            </div>

                            <div style={styles.field}>
                                <label style={styles.label}>
                                    Área jurídica *
                                </label>

                                <input
                                    name="area_juridica"
                                    value={formData.area_juridica}
                                    onChange={handleChange}
                                    style={styles.input}
                                    placeholder="Ex.: Direito Civil"
                                    required
                                    maxLength={100}
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
                                    style={{
                                        ...styles.input,
                                        minHeight: '105px',
                                        resize: 'vertical',
                                    }}
                                    placeholder="Descreva as informações iniciais do caso..."
                                    required
                                />
                            </div>

                            <div style={styles.field}>
                                <label style={styles.label}>
                                    Data de abertura *
                                </label>

                                <input
                                    type="date"
                                    name="data_abertura"
                                    value={formData.data_abertura}
                                    onChange={handleChange}
                                    style={styles.input}
                                    required
                                />
                            </div>

                            {error && (
                                <div
                                    role="alert"
                                    style={{
                                        color: '#B42318',
                                        background: '#FEF3F2',
                                        padding: '12px',
                                        borderRadius: '7px',
                                        marginBottom: '15px',
                                        fontSize: '13px',
                                    }}
                                >
                                    {error}
                                </div>
                            )}

                            <footer style={{
                                display: 'flex',
                                justifyContent: 'flex-end',
                                gap: '10px',
                                flexWrap: 'wrap',
                                marginTop: '22px',
                            }}>
                                <button
                                    type="button"
                                    onClick={fecharFormulario}
                                    disabled={saving}
                                    style={styles.secondaryButton}
                                >
                                    Cancelar
                                </button>

                                <button
                                    type="submit"
                                    disabled={saving || assistidosAtivos.length === 0}
                                    style={{
                                        ...styles.button,
                                        opacity: saving || assistidosAtivos.length === 0
                                            ? 0.6
                                            : 1,
                                    }}
                                >
                                    {saving ? 'Salvando...' : 'Cadastrar caso'}
                                </button>
                            </footer>
                        </form>
                    </section>
                </div>
            )}

            {casoSelecionado && (
                <div
                    style={styles.modalOverlay}
                    onClick={() => setCasoSelecionado(null)}
                >
                    <section
                        style={styles.modal}
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="titulo-detalhes-caso"
                        onClick={(event) => event.stopPropagation()}
                    >
                        <header style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            marginBottom: '20px',
                        }}>
                            <div>
                                <span style={styles.eyebrow}>
                                    DETALHES DO REGISTRO
                                </span>

                                <h2
                                    id="titulo-detalhes-caso"
                                    style={{
                                        color: '#003874',
                                        fontSize: '21px',
                                        margin: '6px 0 0',
                                    }}
                                >
                                    {casoSelecionado.codigo_interno}
                                </h2>
                            </div>

                            <button
                                type="button"
                                onClick={() => setCasoSelecionado(null)}
                                aria-label="Fechar detalhes"
                                style={{
                                    border: 'none',
                                    background: 'transparent',
                                    cursor: 'pointer',
                                    color: '#667085',
                                }}
                            >
                                <X size={21} />
                            </button>
                        </header>

                        <div style={{ display: 'grid', gap: '15px' }}>
                            <div>
                                <strong>Título / assunto</strong>
                                <p>{casoSelecionado.titulo_assunto}</p>
                            </div>

                            <div>
                                <strong>Assistido</strong>
                                <p>
                                    {obterNomeAssistido(casoSelecionado.id_assistido)}
                                </p>
                            </div>

                            <div>
                                <strong>Área jurídica</strong>
                                <p>{casoSelecionado.area_juridica}</p>
                            </div>

                            <div>
                                <strong>Situação</strong>
                                <p>{casoSelecionado.situacao}</p>
                            </div>

                            <div>
                                <strong>Data de abertura</strong>
                                <p>{formatarData(casoSelecionado.data_abertura)}</p>
                            </div>

                            <div>
                                <strong>Data de encerramento</strong>
                                <p>
                                    {formatarData(casoSelecionado.data_encerramento)}
                                </p>
                            </div>

                            <div>
                                <strong>Descrição</strong>
                                <p style={{ whiteSpace: 'pre-wrap' }}>
                                    {casoSelecionado.descricao}
                                </p>
                            </div>
                        </div>

                        {validationError && (
                            <div
                                role="alert"
                                style={{
                                    color: '#B42318',
                                    background: '#FEF3F2',
                                    padding: '12px',
                                    borderRadius: '7px',
                                    marginTop: '15px',
                                    fontSize: '13px',
                                }}
                            >
                                {validationError}
                            </div>
                        )}

                        <footer style={{
                            display: 'flex',
                            justifyContent: 'flex-end',
                            gap: '10px',
                            flexWrap: 'wrap',
                            marginTop: '20px',
                        }}>
                            {perfil === 'Professor' &&
                                casoSelecionado.situacao === 'Em triagem' && (
                                    <button
                                        type="button"
                                        onClick={validarCaso}
                                        disabled={saving}
                                        style={{
                                            ...styles.button,
                                            background: '#16803C',
                                            opacity: saving ? 0.6 : 1,
                                        }}
                                    >
                                        {saving ? 'Validando...' : 'Validar caso'}
                                    </button>
                                )}

                            <button
                                type="button"
                                onClick={() => {
                                    if (!saving) {
                                        setCasoSelecionado(null);
                                        setValidationError('');
                                    }
                                }}
                                disabled={saving}
                                style={styles.secondaryButton}
                            >
                                Fechar
                            </button>
                        </footer>
                    </section>
                </div>
            )}

            {associacaoOpen && (
                <div
                    style={styles.modalOverlay}
                    onClick={() => {
                        if (!saving) setAssociacaoOpen(false);
                    }}
                >
                    <section
                        style={styles.modal}
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="titulo-associacao"
                        onClick={(event) => event.stopPropagation()}
                    >
                        <header style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            marginBottom: '20px',
                        }}>
                            <div>
                                <span style={styles.eyebrow}>
                                    GESTÃO DE CASOS
                                </span>

                                <h2
                                    id="titulo-associacao"
                                    style={{
                                        color: '#003874',
                                        fontSize: '21px',
                                        margin: '6px 0 0',
                                    }}
                                >
                                    Associar professor orientador
                                </h2>
                            </div>

                            <button
                                type="button"
                                onClick={() => setAssociacaoOpen(false)}
                                disabled={saving}
                                aria-label="Fechar"
                                style={{
                                    border: 'none',
                                    background: 'transparent',
                                    cursor: 'pointer',
                                    color: '#667085',
                                }}
                            >
                                <X size={21} />
                            </button>
                        </header>

                        <p style={{ color: '#667085', fontSize: '14px' }}>
                            Caso: <strong>
                                {casoParaAssociar?.codigo_interno}
                            </strong>
                        </p>

                        <div style={styles.field}>
                            <label style={styles.label}>
                                Professor orientador
                            </label>

                            <select
                                value={professorSelecionado}
                                onChange={(event) =>
                                    setProfessorSelecionado(event.target.value)
                                }
                                style={{
                                    ...styles.input,
                                    width: '100%',
                                    boxSizing: 'border-box',
                                }}
                                disabled={saving}
                            >
                                <option value="">Selecione um professor</option>

                                {professores.map((professor) => (
                                    <option
                                        key={professor.id_professor}
                                        value={professor.id_professor}
                                    >
                                        Matrícula funcional: {professor.identificacao_funcional}
                                        {professor.area_vinculo
                                            ? ` — ${professor.area_vinculo}`
                                            : ''}
                                    </option>
                                ))}
                            </select>

                            {professores.length === 0 && (
                                <p style={{
                                    color: '#A15C00',
                                    fontSize: '13px',
                                    marginTop: '8px',
                                }}>
                                    Não há professores ativos disponíveis para associação.
                                </p>
                            )}
                        </div>

                        {associationError && (
                            <div style={{
                                background: '#FEF3F2',
                                color: '#B42318',
                                padding: '11px',
                                borderRadius: '7px',
                                fontSize: '13px',
                                marginBottom: '15px',
                            }}>
                                {associationError}
                            </div>
                        )}

                        <footer style={{
                            display: 'flex',
                            justifyContent: 'flex-end',
                            gap: '10px',
                            marginTop: '22px',
                        }}>
                            <button
                                type="button"
                                onClick={() => setAssociacaoOpen(false)}
                                disabled={saving}
                                style={styles.secondaryButton}
                            >
                                Cancelar
                            </button>

                            <button
                                type="button"
                                onClick={salvarAssociacaoProfessor}
                                disabled={saving || professores.length === 0}
                                style={{
                                    ...styles.button,
                                    opacity: saving || professores.length === 0
                                        ? 0.6
                                        : 1,
                                }}
                            >
                                {saving ? 'Salvando...' : 'Salvar associação'}
                            </button>
                        </footer>
                    </section>
                </div>
            )}
        </main>
    );
}
