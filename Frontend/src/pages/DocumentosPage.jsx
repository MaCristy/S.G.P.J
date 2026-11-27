
import { useEffect, useMemo, useState } from 'react';
import {
    FileText,
    Upload,
    Download,
    Search,
    RefreshCw,
    X,
    FolderOpen,
} from 'lucide-react';

import {
    listarDocumentos,
    enviarDocumento,
    baixarDocumento,
} from '../services/documentosService.js';

import { listarCasosJuridicos } from '../services/casosJuridicosService.js';
import { listarAtendimentos } from '../services/atendimentosService.js';
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
    item: {
        padding: '18px 20px',
        borderBottom: '1px solid #EAECF0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '15px',
    },
    icon: {
        background: '#EAF2FB',
        color: '#003874',
        borderRadius: '9px',
        padding: '12px',
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
        maxWidth: '600px',
        maxHeight: '90vh',
        overflowY: 'auto',
        boxSizing: 'border-box',
    },
    empty: {
        textAlign: 'center',
        padding: '45px 20px',
        color: '#667085',
    },
};

function formatarData(data) {
    if (!data) return 'Data não informada';

    const valor = new Date(data);

    if (Number.isNaN(valor.getTime())) {
        return data;
    }

    return valor.toLocaleString('pt-BR');
}

export default function DocumentosPage() {
    const { user } = useAuth();

    const perfil = user?.perfil;
    const podeEnviar = perfil === 'Gestão' || perfil === 'Aluno';

    const [documentos, setDocumentos] = useState([]);
    const [casos, setCasos] = useState([]);
    const [atendimentos, setAtendimentos] = useState([]);

    const [busca, setBusca] = useState('');
    const [filtroVinculo, setFiltroVinculo] = useState('todos');

    const [modalAberto, setModalAberto] = useState(false);
    const [arquivo, setArquivo] = useState(null);
    const [idCaso, setIdCaso] = useState('');
    const [idAtendimento, setIdAtendimento] = useState('');
    const [classificacao, setClassificacao] = useState('');

    const [carregando, setCarregando] = useState(true);
    const [enviando, setEnviando] = useState(false);
    const [baixandoId, setBaixandoId] = useState(null);
    const [erro, setErro] = useState('');
    const [sucesso, setSucesso] = useState('');

    async function carregarDados() {
        setCarregando(true);
        setErro('');

        try {
            const [listaDocumentos, listaCasos, listaAtendimentos] =
                await Promise.all([
                    listarDocumentos(),
                    listarCasosJuridicos(),
                    listarAtendimentos(),
                ]);

            setDocumentos(Array.isArray(listaDocumentos) ? listaDocumentos : []);
            setCasos(Array.isArray(listaCasos) ? listaCasos : []);
            setAtendimentos(
                Array.isArray(listaAtendimentos) ? listaAtendimentos : []
            );
        } catch (error) {
            setErro(error.message || 'Não foi possível carregar os documentos.');
        } finally {
            setCarregando(false);
        }
    }

    useEffect(() => {
        carregarDados();
    }, []);

    const documentosFiltrados = useMemo(() => {
        return documentos.filter((documento) => {
            const nome = documento.nome || '';
            const termo = busca.toLowerCase();

            const correspondeBusca =
                nome.toLowerCase().includes(termo) ||
                String(documento.id_documento).includes(termo) ||
                String(documento.id_caso || '').includes(termo) ||
                String(documento.id_atendimento || '').includes(termo);

            let correspondeVinculo = true;

            if (filtroVinculo === 'caso') {
                correspondeVinculo = documento.id_caso !== null;
            } else if (filtroVinculo === 'atendimento') {
                correspondeVinculo = documento.id_atendimento !== null;
            }

            return correspondeBusca && correspondeVinculo;
        });
    }, [documentos, busca, filtroVinculo]);

    function abrirModal() {
        setArquivo(null);
        setIdCaso('');
        setIdAtendimento('');
        setClassificacao('');
        setErro('');
        setSucesso('');
        setModalAberto(true);
    }

    async function handleEnviar(event) {
        event.preventDefault();

        setErro('');
        setSucesso('');

        if (!arquivo) {
            setErro('Selecione um arquivo PDF para enviar.');
            return;
        }

        if (!idCaso && !idAtendimento) {
            setErro('Vincule o documento a um caso ou atendimento.');
            return;
        }

        if (!arquivo.name.toLowerCase().endsWith('.pdf')) {
            setErro('Apenas arquivos PDF são permitidos.');
            return;
        }

        setEnviando(true);

        try {
            await enviarDocumento({
                arquivo,
                idCaso: idCaso ? Number(idCaso) : null,
                idAtendimento: idAtendimento
                    ? Number(idAtendimento)
                    : null,
                classificacaoAcesso: classificacao.trim() || null,
            });

            setSucesso('Documento enviado com sucesso!');
            setModalAberto(false);
            setArquivo(null);
            setIdCaso('');
            setIdAtendimento('');
            setClassificacao('');

            await carregarDados();
        } catch (error) {
            setErro(error.message || 'Não foi possível enviar o documento.');
        } finally {
            setEnviando(false);
        }
    }

    async function handleBaixar(documento) {
        setErro('');
        setBaixandoId(documento.id_documento);

        try {
            const arquivoBlob = await baixarDocumento(documento.id_documento);
            const url = window.URL.createObjectURL(arquivoBlob);

            const link = document.createElement('a');
            link.href = url;
            link.download = documento.nome || 'documento.pdf';

            document.body.appendChild(link);
            link.click();
            link.remove();

            window.URL.revokeObjectURL(url);
        } catch (error) {
            setErro(error.message || 'Não foi possível baixar o documento.');
        } finally {
            setBaixandoId(null);
        }
    }

    return (
        <div style={styles.page}>
            <div style={styles.heading}>
                <div>
                    <span style={styles.eyebrow}>GESTÃO DOCUMENTAL</span>
                    <h1 style={styles.title}>Documentos</h1>
                    <p style={styles.subtitle}>
                        Consulte e organize os documentos vinculados aos casos e atendimentos.
                    </p>
                </div>

                {podeEnviar && (
                    <button style={styles.button} onClick={abrirModal}>
                        <Upload size={18} />
                        Enviar documento
                    </button>
                )}
            </div>

            {erro && (
                <div style={{
                    padding: '13px 16px',
                    marginBottom: '15px',
                    borderRadius: '8px',
                    background: '#FEF3F2',
                    color: '#B42318',
                    fontSize: '14px',
                }}>
                    {erro}
                </div>
            )}

            {sucesso && (
                <div style={{
                    padding: '13px 16px',
                    marginBottom: '15px',
                    borderRadius: '8px',
                    background: '#ECFDF3',
                    color: '#16803C',
                    fontSize: '14px',
                }}>
                    {sucesso}
                </div>
            )}

            <section style={styles.panel}>
                <div style={styles.panelHeading}>
                    <div>
                        <h2 style={{ margin: 0, color: '#202938', fontSize: '17px' }}>
                            Arquivos cadastrados
                        </h2>
                        <p style={{ margin: '5px 0 0', color: '#667085', fontSize: '13px' }}>
                            {documentos.length} documento(s) disponível(is) para seu perfil
                        </p>
                    </div>

                    <button
                        type="button"
                        style={styles.secondaryButton}
                        onClick={carregarDados}
                        disabled={carregando}
                    >
                        <RefreshCw size={16} />
                        Atualizar
                    </button>
                </div>

                <div style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '12px',
                    padding: '18px 20px',
                }}>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '9px',
                        border: '1px solid #D9DEE8',
                        borderRadius: '8px',
                        padding: '0 12px',
                        flex: '1 1 250px',
                    }}>
                        <Search size={17} color="#667085" />
                        <input
                            type="text"
                            placeholder="Buscar por nome ou identificador..."
                            value={busca}
                            onChange={(event) => setBusca(event.target.value)}
                            style={{
                                border: 'none',
                                outline: 'none',
                                padding: '12px 0',
                                width: '100%',
                                fontSize: '14px',
                            }}
                        />
                    </div>

                    <select
                        value={filtroVinculo}
                        onChange={(event) => setFiltroVinculo(event.target.value)}
                        style={{ ...styles.input, width: 'auto', minWidth: '190px' }}
                    >
                        <option value="todos">Todos os vínculos</option>
                        <option value="caso">Documentos de casos</option>
                        <option value="atendimento">Documentos de atendimentos</option>
                    </select>
                </div>

                {carregando ? (
                    <div style={styles.empty}>Carregando documentos...</div>
                ) : documentosFiltrados.length === 0 ? (
                    <div style={styles.empty}>
                        <FolderOpen size={35} />
                        <p style={{ fontWeight: '600', color: '#344054' }}>
                            Nenhum documento encontrado
                        </p>
                        <p style={{ fontSize: '13px' }}>
                            Os documentos disponíveis para seu perfil aparecerão aqui.
                        </p>
                    </div>
                ) : (
                    documentosFiltrados.map((documento) => (
                        <div key={documento.id_documento} style={styles.item}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flex: 1 }}>
                                <div style={styles.icon}>
                                    <FileText size={23} />
                                </div>

                                <div style={{ minWidth: 0 }}>
                                    <strong style={{
                                        display: 'block',
                                        color: '#202938',
                                        fontSize: '14px',
                                        overflowWrap: 'anywhere',
                                    }}>
                                        {documento.nome}
                                    </strong>

                                    <div style={{
                                        display: 'flex',
                                        flexWrap: 'wrap',
                                        gap: '8px 15px',
                                        marginTop: '7px',
                                        color: '#667085',
                                        fontSize: '12px',
                                    }}>
                                        <span>Documento #{documento.id_documento}</span>
                                        <span>{formatarData(documento.data_inclusao)}</span>
                                        {documento.id_caso && (
                                            <span>Caso #{documento.id_caso}</span>
                                        )}
                                        {documento.id_atendimento && (
                                            <span>Atendimento #{documento.id_atendimento}</span>
                                        )}
                                        {documento.classificacao_acesso && (
                                            <span>Acesso: {documento.classificacao_acesso}</span>
                                        )}
                                    </div>
                                </div>
                            </div>

                            <button
                                type="button"
                                style={styles.secondaryButton}
                                onClick={() => handleBaixar(documento)}
                                disabled={baixandoId === documento.id_documento}
                            >
                                <Download size={16} />
                                {baixandoId === documento.id_documento
                                    ? 'Baixando...'
                                    : 'Baixar PDF'}
                            </button>
                        </div>
                    ))
                )}
            </section>

            {modalAberto && (
                <div style={styles.modalOverlay}>
                    <div style={styles.modal}>
                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            marginBottom: '22px',
                        }}>
                            <div>
                                <h2 style={{ color: '#003874', margin: 0, fontSize: '21px' }}>
                                    Enviar documento
                                </h2>
                                <p style={{ color: '#667085', fontSize: '13px', marginBottom: 0 }}>
                                    Selecione um PDF e informe seu vínculo.
                                </p>
                            </div>

                            <button
                                type="button"
                                onClick={() => setModalAberto(false)}
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

                        <form onSubmit={handleEnviar}>
                            <div style={styles.field}>
                                <label style={styles.label} htmlFor="arquivo">
                                    Arquivo PDF *
                                </label>
                                <input
                                    id="arquivo"
                                    type="file"
                                    accept=".pdf,application/pdf"
                                    onChange={(event) => setArquivo(event.target.files?.[0] || null)}
                                    style={styles.input}
                                    required
                                />
                                <small style={{ color: '#667085' }}>
                                    O backend verifica o formato e o tamanho do arquivo.
                                </small>
                            </div>

                            <div style={styles.field}>
                                <label style={styles.label} htmlFor="idCaso">
                                    Caso jurídico
                                </label>
                                <select
                                    id="idCaso"
                                    value={idCaso}
                                    onChange={(event) => setIdCaso(event.target.value)}
                                    style={styles.input}
                                >
                                    <option value="">Não vincular a um caso</option>
                                    {casos.map((caso) => (
                                        <option key={caso.id_caso} value={caso.id_caso}>
                                            {caso.codigo_interno} — {caso.titulo_assunto}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div style={styles.field}>
                                <label style={styles.label} htmlFor="idAtendimento">
                                    Atendimento
                                </label>
                                <select
                                    id="idAtendimento"
                                    value={idAtendimento}
                                    onChange={(event) => setIdAtendimento(event.target.value)}
                                    style={styles.input}
                                >
                                    <option value="">Não vincular a um atendimento</option>
                                    {atendimentos.map((atendimento) => (
                                        <option
                                            key={atendimento.id_atendimento}
                                            value={atendimento.id_atendimento}
                                        >
                                            Atendimento #{atendimento.id_atendimento}
                                            {' — '}
                                            {atendimento.descricao_objetiva || 'Sem descrição'}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div style={styles.field}>
                                <label style={styles.label} htmlFor="classificacao">
                                    Classificação de acesso (opcional)
                                </label>
                                <input
                                    id="classificacao"
                                    type="text"
                                    value={classificacao}
                                    onChange={(event) => setClassificacao(event.target.value)}
                                    placeholder="Ex.: Restrito, Interno..."
                                    maxLength={50}
                                    style={styles.input}
                                />
                            </div>

                            <p style={{ color: '#667085', fontSize: '12px', marginTop: 0 }}>
                                O documento precisa estar vinculado a pelo menos um caso jurídico
                                ou atendimento. É possível selecionar os dois.
                            </p>

                            {erro && (
                                <p style={{ color: '#B42318', fontSize: '13px' }}>
                                    {erro}
                                </p>
                            )}

                            <div style={{
                                display: 'flex',
                                justifyContent: 'flex-end',
                                gap: '10px',
                                marginTop: '22px',
                            }}>
                                <button
                                    type="button"
                                    style={styles.secondaryButton}
                                    onClick={() => setModalAberto(false)}
                                >
                                    Cancelar
                                </button>

                                <button
                                    type="submit"
                                    style={styles.button}
                                    disabled={enviando}
                                >
                                    <Upload size={16} />
                                    {enviando ? 'Enviando...' : 'Enviar documento'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
