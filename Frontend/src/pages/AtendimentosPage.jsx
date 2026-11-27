
import { useEffect, useState } from 'react';
import {
    Search,
    Plus,
    CalendarDays,
    ClipboardList,
    UserRound,
    X,
    FileText,
    RefreshCw,
} from 'lucide-react';

import { apiRequest } from '../services/api.js';
import { useAuth } from '../contexts/AuthContext.jsx';

// Define os estilos básicos da página seguindo a identidade visual do S.G.P.J.
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
        padding: '20px',
        borderBottom: '1px solid #D9DEE8',
    },
    search: {
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        background: '#FFFFFF',
        border: '1px solid #D9DEE8',
        borderRadius: '8px',
        padding: '12px 14px',
        maxWidth: '520px',
        width: '100%',
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
    item: {
        padding: '18px 20px',
        borderBottom: '1px solid #EAECF0',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '14px',
    },
    icon: {
        background: '#EAF2FB',
        color: '#003874',
        borderRadius: '9px',
        padding: '11px',
        flexShrink: 0,
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

// Formata a data recebida pela API para exibição em português.
function formatarData(data) {
    if (!data) return 'Data não informada';

    const valor = new Date(data);

    if (Number.isNaN(valor.getTime())) {
        return data;
    }

    return valor.toLocaleString('pt-BR');
}

// Converte a data atual para o formato aceito pelo campo datetime-local.
function obterDataAtual() {
    const agora = new Date();
    const deslocamento = agora.getTimezoneOffset() * 60000;

    return new Date(agora.getTime() - deslocamento)
        .toISOString()
        .slice(0, 16);
}

export default function AtendimentosPage() {
    const { user } = useAuth();

    const perfil = user?.perfil;
    const podeRegistrar = perfil === 'Gestão' || perfil === 'Aluno';

    const [atendimentos, setAtendimentos] = useState([]);
    const [assistidos, setAssistidos] = useState([]);

    const [searchTerm, setSearchTerm] = useState('');
    const [modalOpen, setModalOpen] = useState(false);

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [validationError, setValidationError] = useState('');

    const [formData, setFormData] = useState({
        id_assistido: '',
        id_caso: '',
        data_hora: obterDataAtual(),
        tipo: '',
        descricao_objetiva: '',
        encaminhamento: '',
    });

    // Carrega os atendimentos e os assistidos disponíveis para o usuário.
    async function carregarDados() {
        setLoading(true);
        setError('');

        try {
            const [dadosAtendimentos, dadosAssistidos] = await Promise.all([
                apiRequest('/atendimentos/'),
                apiRequest('/assistidos/'),
            ]);

            setAtendimentos(
                Array.isArray(dadosAtendimentos) ? dadosAtendimentos : []
            );

            setAssistidos(
                Array.isArray(dadosAssistidos) ? dadosAssistidos : []
            );
        } catch (erro) {
            setError(erro.message || 'Não foi possível carregar os dados.');
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        carregarDados();
    }, []);

    // Atualiza os campos do formulário conforme o usuário digita.
    function handleChange(event) {
        const { name, value } = event.target;

        setFormData((anterior) => ({
            ...anterior,
            [name]: value,
        }));
    }

    // Limpa os campos e abre o formulário de registro.
    function abrirFormulario() {
        setFormData({
            id_assistido: '',
            id_caso: '',
            data_hora: obterDataAtual(),
            tipo: '',
            descricao_objetiva: '',
            encaminhamento: '',
        });

        setError('');
        setSuccess('');
        setModalOpen(true);
    }

    // Fecha o formulário sem alterar os registros existentes.
    function fecharFormulario() {
        if (saving) return;

        setModalOpen(false);
        setError('');
    }

    // Envia um novo atendimento para o backend.
    async function handleSubmit(event) {
        event.preventDefault();

        setSaving(true);
        setError('');
        setSuccess('');

        const dadosParaAPI = {
            id_assistido: Number(formData.id_assistido),
            id_caso: formData.id_caso
                ? Number(formData.id_caso)
                : null,
            data_hora: `${formData.data_hora}:00`,
            tipo: formData.tipo.trim(),
            descricao_objetiva: formData.descricao_objetiva.trim(),
            encaminhamento: formData.encaminhamento.trim() || null,
        };

        try {
            await apiRequest('/atendimentos/', {
                method: 'POST',
                body: JSON.stringify(dadosParaAPI),
            });

            setModalOpen(false);
            setSuccess('Atendimento registrado com sucesso!');

            await carregarDados();
        } catch (erro) {
            setError(erro.message || 'Não foi possível registrar o atendimento.');
        } finally {
            setSaving(false);
        }
    }

    // Relaciona cada atendimento ao nome do assistido correspondente.
    function obterNomeAssistido(idAssistido) {
        const assistido = assistidos.find(
            (item) => item.id_assistido === idAssistido
        );

        return assistido?.nome_completo || `Assistido #${idAssistido}`;
    }

    // Filtra os atendimentos pelo nome do assistido e pelos dados do registro.
    const atendimentosFiltrados = atendimentos.filter((item) => {
        const nome = obterNomeAssistido(item.id_assistido);

        const texto = [
            nome,
            item.tipo,
            item.descricao_objetiva,
            item.encaminhamento,
        ]
            .filter(Boolean)
            .join(' ')
            .toLowerCase();

        return texto.includes(searchTerm.toLowerCase());
    });

    return (
        <main style={styles.page}>
            <header style={styles.heading}>
                <div>
                    <span style={styles.eyebrow}>GESTÃO DA PRÁTICA JURÍDICA</span>
                    <h1 style={styles.title}>Atendimentos</h1>
                    <p style={styles.subtitle}>
                        Consulte e registre os atendimentos realizados no núcleo jurídico.
                    </p>
                </div>

                {podeRegistrar && (
                    <button
                        type="button"
                        style={styles.button}
                        onClick={abrirFormulario}
                    >
                        <Plus size={18} />
                        Novo atendimento
                    </button>
                )}
            </header>

            <section style={styles.search}>
                <Search size={19} color="#667085" />

                <input
                    type="search"
                    aria-label="Pesquisar atendimentos"
                    placeholder="Pesquisar por assistido, tipo ou descrição..."
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
                            Histórico de atendimentos
                        </h2>
                        <p style={{ color: '#667085', fontSize: '13px', margin: 0 }}>
                            Registros disponíveis conforme seu perfil de acesso.
                        </p>
                    </div>

                    <button
                        type="button"
                        onClick={carregarDados}
                        title="Atualizar lista"
                        aria-label="Atualizar lista"
                        style={{
                            border: 'none',
                            background: 'transparent',
                            color: '#003874',
                            cursor: 'pointer',
                        }}
                    >
                        <RefreshCw size={19} />
                    </button>
                </div>

                {loading ? (
                    <div style={styles.empty}>
                        <p>Carregando atendimentos...</p>
                    </div>
                ) : atendimentosFiltrados.length > 0 ? (
                    atendimentosFiltrados.map((item) => (
                        <article
                            key={item.id_atendimento}
                            style={styles.item}
                        >
                            <div style={styles.icon}>
                                <ClipboardList size={22} />
                            </div>

                            <div style={{ flex: 1, minWidth: 0 }}>
                                <div
                                    style={{
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        flexWrap: 'wrap',
                                        gap: '8px',
                                    }}
                                >
                                    <strong style={{ color: '#003874', fontSize: '15px' }}>
                                        {item.tipo}
                                    </strong>

                                    <span
                                        style={{
                                            fontSize: '12px',
                                            color: '#667085',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '5px',
                                        }}
                                    >
                                        <CalendarDays size={14} />
                                        {formatarData(item.data_hora)}
                                    </span>
                                </div>

                                <p
                                    style={{
                                        fontSize: '13px',
                                        color: '#344054',
                                        margin: '10px 0',
                                    }}
                                >
                                    <UserRound
                                        size={14}
                                        style={{ verticalAlign: 'middle', marginRight: '5px' }}
                                    />
                                    {obterNomeAssistido(item.id_assistido)}
                                </p>

                                <p
                                    style={{
                                        fontSize: '14px',
                                        lineHeight: '1.6',
                                        margin: '8px 0',
                                        color: '#475467',
                                    }}
                                >
                                    {item.descricao_objetiva}
                                </p>

                                {item.id_caso && (
                                    <span
                                        style={{
                                            display: 'inline-block',
                                            background: '#EAF2FB',
                                            color: '#003874',
                                            borderRadius: '5px',
                                            padding: '5px 8px',
                                            fontSize: '12px',
                                            marginTop: '5px',
                                        }}
                                    >
                                        Caso jurídico #{item.id_caso}
                                    </span>
                                )}

                                {item.encaminhamento && (
                                    <p
                                        style={{
                                            fontSize: '13px',
                                            color: '#667085',
                                            marginTop: '10px',
                                        }}
                                    >
                                        <FileText
                                            size={14}
                                            style={{ verticalAlign: 'middle', marginRight: '5px' }}
                                        />
                                        Encaminhamento: {item.encaminhamento}
                                    </p>
                                )}
                            </div>
                        </article>
                    ))
                ) : (
                    <div style={styles.empty}>
                        <ClipboardList
                            size={38}
                            color="#98A2B3"
                            style={{ marginBottom: '12px' }}
                        />

                        <strong style={{ display: 'block', color: '#344054' }}>
                            {searchTerm
                                ? 'Nenhum atendimento encontrado'
                                : 'Nenhum atendimento registrado'}
                        </strong>

                        <p style={{ fontSize: '13px' }}>
                            {searchTerm
                                ? 'Tente pesquisar utilizando outros termos.'
                                : 'Os atendimentos registrados serão apresentados nesta área.'}
                        </p>
                    </div>
                )}
            </section>

            {modalOpen && (
                <div style={styles.modalOverlay}>
                    <section
                        style={styles.modal}
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="atendimento-modal-title"
                    >
                        <header
                            style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'flex-start',
                                gap: '15px',
                                marginBottom: '24px',
                            }}
                        >
                            <div>
                                <span style={styles.eyebrow}>NOVO REGISTRO</span>

                                <h2
                                    id="atendimento-modal-title"
                                    style={{ color: '#003874', margin: '7px 0' }}
                                >
                                    Registrar atendimento
                                </h2>

                                <p style={styles.subtitle}>
                                    Informe os dados do atendimento realizado.
                                </p>
                            </div>

                            <button
                                type="button"
                                onClick={fecharFormulario}
                                aria-label="Fechar formulário"
                                disabled={saving}
                                style={{
                                    background: 'transparent',
                                    border: 'none',
                                    cursor: 'pointer',
                                    color: '#667085',
                                }}
                            >
                                <X size={22} />
                            </button>
                        </header>

                        <form onSubmit={handleSubmit}>
                            <div style={styles.field}>
                                <label style={styles.label} htmlFor="id_assistido">
                                    Assistido *
                                </label>

                                <select
                                    id="id_assistido"
                                    name="id_assistido"
                                    value={formData.id_assistido}
                                    onChange={handleChange}
                                    required
                                    style={styles.input}
                                >
                                    <option value="">Selecione um assistido</option>

                                    {assistidos.map((assistido) => (
                                        <option
                                            key={assistido.id_assistido}
                                            value={assistido.id_assistido}
                                        >
                                            {assistido.nome_completo}
                                        </option>
                                    ))}
                                </select>

                                {assistidos.length === 0 && (
                                    <small style={{ color: '#B42318' }}>
                                        Não há assistidos disponíveis para seleção.
                                    </small>
                                )}
                            </div>

                            <div style={styles.field}>
                                <label style={styles.label} htmlFor="data_hora">
                                    Data e horário *
                                </label>

                                <input
                                    id="data_hora"
                                    name="data_hora"
                                    type="datetime-local"
                                    value={formData.data_hora}
                                    onChange={handleChange}
                                    required
                                    style={styles.input}
                                />
                            </div>

                            <div style={styles.field}>
                                <label style={styles.label} htmlFor="tipo">
                                    Tipo de atendimento *
                                </label>

                                <input
                                    id="tipo"
                                    name="tipo"
                                    type="text"
                                    maxLength={80}
                                    placeholder="Ex.: Orientação jurídica, consulta..."
                                    value={formData.tipo}
                                    onChange={handleChange}
                                    required
                                    style={styles.input}
                                />
                            </div>

                            <div style={styles.field}>
                                <label style={styles.label} htmlFor="id_caso">
                                    Número do caso jurídico (opcional)
                                </label>

                                <input
                                    id="id_caso"
                                    name="id_caso"
                                    type="number"
                                    min="1"
                                    placeholder="Informe o ID do caso, se houver"
                                    value={formData.id_caso}
                                    onChange={handleChange}
                                    style={styles.input}
                                />

                                <small style={{ color: '#667085', fontSize: '12px' }}>
                                    O caso precisa pertencer ao assistido selecionado e estar
                                    disponível para seu perfil.
                                </small>
                            </div>

                            <div style={styles.field}>
                                <label style={styles.label} htmlFor="descricao_objetiva">
                                    Descrição objetiva *
                                </label>

                                <textarea
                                    id="descricao_objetiva"
                                    name="descricao_objetiva"
                                    rows={4}
                                    placeholder="Descreva os assuntos tratados durante o atendimento..."
                                    value={formData.descricao_objetiva}
                                    onChange={handleChange}
                                    required
                                    style={{
                                        ...styles.input,
                                        resize: 'vertical',
                                    }}
                                />
                            </div>

                            <div style={styles.field}>
                                <label style={styles.label} htmlFor="encaminhamento">
                                    Encaminhamento
                                </label>

                                <textarea
                                    id="encaminhamento"
                                    name="encaminhamento"
                                    rows={3}
                                    placeholder="Informe as orientações ou providências definidas..."
                                    value={formData.encaminhamento}
                                    onChange={handleChange}
                                    style={{
                                        ...styles.input,
                                        resize: 'vertical',
                                    }}
                                />
                            </div>

                            {error && (
                                <p
                                    role="alert"
                                    style={{
                                        color: '#B42318',
                                        background: '#FEF3F2',
                                        padding: '10px',
                                        borderRadius: '6px',
                                        fontSize: '13px',
                                    }}
                                >
                                    {error}
                                </p>
                            )}

                            <div
                                style={{
                                    display: 'flex',
                                    justifyContent: 'flex-end',
                                    gap: '10px',
                                    flexWrap: 'wrap',
                                    marginTop: '24px',
                                }}
                            >
                                <button
                                    type="button"
                                    onClick={fecharFormulario}
                                    disabled={saving}
                                    style={{
                                        background: '#FFFFFF',
                                        border: '1px solid #D9DEE8',
                                        color: '#344054',
                                        borderRadius: '7px',
                                        padding: '11px 16px',
                                        cursor: 'pointer',
                                    }}
                                >
                                    Cancelar
                                </button>

                                <button
                                    type="submit"
                                    disabled={saving || assistidos.length === 0}
                                    style={{
                                        ...styles.button,
                                        opacity: saving || assistidos.length === 0 ? 0.6 : 1,
                                    }}
                                >
                                    <Plus size={17} />
                                    {saving ? 'Salvando...' : 'Registrar atendimento'}
                                </button>
                            </div>
                        </form>
                    </section>
                </div>
            )}
        </main>
    );
}
