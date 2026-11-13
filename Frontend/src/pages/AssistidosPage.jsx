
import { useEffect, useState } from 'react';
import {
    Search,
    Plus,
    Users,
    X,
    UserRound,
    Pencil,
} from 'lucide-react';

import {
    listarAssistidos,
    criarAssistido,
    atualizarAssistido,
} from '../services/assistidosService.js';

export default function AssistidosPage() {
    const [modalOpen, setModalOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [assistidos, setAssistidos] = useState([]);
    const [editingId, setEditingId] = useState(null);

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');

    const [formData, setFormData] = useState({
        nome: '',
        identificador: '',
        contato: '',
        endereco: '',
        observacoes: '',
    });

    // Converte os nomes dos campos da API para o formato da interface.
    function formatarAssistido(dado) {
        return {
            id: dado.id_assistido,
            nome: dado.nome_completo,
            identificador: dado.identificador_cadastral,
            contato: dado.contato,
            endereco: dado.endereco || '',
            observacoes: dado.observacoes_administrativas || '',
            situacao: dado.situacao,
        };
    }

    // Carrega os assistidos cadastrados no banco de dados.
    async function carregarAssistidos() {
        try {
            setError('');
            const dados = await listarAssistidos();

            setAssistidos(dados.map(formatarAssistido));
        } catch (erro) {
            setError(erro.message);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        carregarAssistidos();
    }, []);

    function handleChange(event) {
        const { name, value } = event.target;

        setFormData((previous) => ({
            ...previous,
            [name]: value,
        }));
    }

    function openNewModal() {
        setEditingId(null);

        setFormData({
            nome: '',
            identificador: '',
            contato: '',
            endereco: '',
            observacoes: '',
        });

        setError('');
        setModalOpen(true);
    }

    function openEditModal(assistido) {
        setEditingId(assistido.id);

        setFormData({
            nome: assistido.nome,
            identificador: assistido.identificador,
            contato: assistido.contato,
            endereco: assistido.endereco,
            observacoes: assistido.observacoes,
        });

        setError('');
        setModalOpen(true);
    }

    function closeModal() {
        setModalOpen(false);
        setEditingId(null);
        setError('');
    }

    // Envia os dados para a API.
    async function handleSubmit(event) {
        event.preventDefault();

        setSaving(true);
        setError('');

        const dadosParaAPI = {
            nome_completo: formData.nome,
            identificador_cadastral: formData.identificador,
            contato: formData.contato,
            endereco: formData.endereco || null,
            observacoes_administrativas: formData.observacoes || null,
        };

        try {
            if (editingId !== null) {
                await atualizarAssistido(editingId, dadosParaAPI);
            } else {
                await criarAssistido({
                    ...dadosParaAPI,
                    situacao: 'Ativo',
                });
            }

            await carregarAssistidos();
            closeModal();
        } catch (erro) {
            setError(erro.message);
        } finally {
            setSaving(false);
        }
    }

    const assistidosFiltrados = assistidos.filter((assistido) =>
        `${assistido.nome} ${assistido.identificador}`
            .toLowerCase()
            .includes(searchTerm.toLowerCase())
    );

    return (
        <main className="assistidos-page">
            <header className="assistidos-heading">
                <div>
                    <span>GESTÃO DE CADASTROS</span>
                    <h1>Assistidos</h1>
                    <p>
                        Consulte e gerencie as pessoas atendidas pela prática jurídica.
                    </p>
                </div>

                <button
                    type="button"
                    className="assistidos-new-button"
                    onClick={openNewModal}
                >
                    <Plus size={18} />
                    Novo assistido
                </button>
            </header>

            <section className="assistidos-toolbar">
                <div className="assistidos-search">
                    <Search size={18} />
                    <input
                        type="search"
                        placeholder="Pesquisar por nome ou identificação..."
                        aria-label="Pesquisar assistidos"
                        value={searchTerm}
                        onChange={(event) => setSearchTerm(event.target.value)}
                    />
                </div>
            </section>

            <section className="assistidos-table-panel">
                <div className="assistidos-table-heading">
                    <div>
                        <h2>Lista de assistidos</h2>
                        <p>Cadastros registrados no sistema.</p>
                    </div>
                    <Users size={22} />
                </div>

                {loading ? (
                    <div className="assistidos-empty">
                        <p>Carregando assistidos...</p>
                    </div>
                ) : error && assistidos.length === 0 ? (
                    <div className="assistidos-empty" role="alert">
                        <strong>Não foi possível carregar os assistidos.</strong>
                        <p>{error}</p>
                        <button
                            type="button"
                            className="assistidos-new-button"
                            onClick={carregarAssistidos}
                        >
                            Tentar novamente
                        </button>
                    </div>
                ) : assistidosFiltrados.length > 0 ? (
                    <div className="assistidos-list">
                        {assistidosFiltrados.map((assistido) => (
                            <div className="assistido-item" key={assistido.id}>
                                <div className="assistido-item-icon">
                                    <UserRound size={20} />
                                </div>

                                <div className="assistido-item-info">
                                    <strong>{assistido.nome}</strong>
                                    <small>
                                        {assistido.identificador} · {assistido.contato}
                                    </small>
                                </div>

                                <button
                                    type="button"
                                    className="assistido-edit-button"
                                    aria-label={`Editar ${assistido.nome}`}
                                    onClick={() => openEditModal(assistido)}
                                >
                                    <Pencil size={16} />
                                </button>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="assistidos-empty">
                        <Users size={35} />
                        <strong>
                            {searchTerm
                                ? 'Nenhum resultado encontrado'
                                : 'Nenhum assistido cadastrado'}
                        </strong>
                        <p>
                            {searchTerm
                                ? 'Tente pesquisar utilizando outro nome ou identificação.'
                                : 'Quando houver cadastros, eles serão apresentados nesta lista.'}
                        </p>
                    </div>
                )}
            </section>

            {error && assistidos.length > 0 && (
                <p role="alert">{error}</p>
            )}

            {modalOpen && (
                <div className="assistido-modal-overlay">
                    <section
                        className="assistido-modal"
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="assistido-modal-title"
                    >
                        <header className="assistido-modal-header">
                            <div>
                                <span>
                                    {editingId !== null
                                        ? 'ATUALIZAÇÃO DE CADASTRO'
                                        : 'NOVO CADASTRO'}
                                </span>

                                <h2 id="assistido-modal-title">
                                    {editingId !== null
                                        ? 'Editar assistido'
                                        : 'Cadastrar assistido'}
                                </h2>

                                <p>
                                    Preencha as informações da pessoa atendida.
                                </p>
                            </div>

                            <button
                                type="button"
                                className="assistido-modal-close"
                                aria-label="Fechar formulário"
                                onClick={closeModal}
                                disabled={saving}
                            >
                                <X size={21} />
                            </button>
                        </header>

                        <form onSubmit={handleSubmit}>
                            <div className="assistido-form-field">
                                <label htmlFor="nome">Nome completo *</label>
                                <input
                                    id="nome"
                                    name="nome"
                                    type="text"
                                    value={formData.nome}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            <div className="assistido-form-field">
                                <label htmlFor="identificador">
                                    Identificador cadastral *
                                </label>
                                <input
                                    id="identificador"
                                    name="identificador"
                                    type="text"
                                    value={formData.identificador}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            <div className="assistido-form-field">
                                <label htmlFor="contato">Contato *</label>
                                <input
                                    id="contato"
                                    name="contato"
                                    type="text"
                                    value={formData.contato}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            <div className="assistido-form-field">
                                <label htmlFor="endereco">Endereço</label>
                                <input
                                    id="endereco"
                                    name="endereco"
                                    type="text"
                                    value={formData.endereco}
                                    onChange={handleChange}
                                />
                            </div>

                            <div className="assistido-form-field">
                                <label htmlFor="observacoes">
                                    Observações administrativas
                                </label>
                                <textarea
                                    id="observacoes"
                                    name="observacoes"
                                    rows="3"
                                    value={formData.observacoes}
                                    onChange={handleChange}
                                />
                            </div>

                            {error && (
                                <p role="alert">{error}</p>
                            )}

                            <footer className="assistido-modal-actions">
                                <button
                                    type="button"
                                    className="assistido-cancel-button"
                                    onClick={closeModal}
                                    disabled={saving}
                                >
                                    Cancelar
                                </button>

                                <button
                                    type="submit"
                                    className="assistidos-new-button"
                                    disabled={saving}
                                >
                                    {saving
                                        ? 'Salvando...'
                                        : editingId !== null
                                            ? 'Salvar alterações'
                                            : 'Cadastrar assistido'}
                                </button>
                            </footer>
                        </form>
                    </section>
                </div>
            )}
        </main>
    );
}
