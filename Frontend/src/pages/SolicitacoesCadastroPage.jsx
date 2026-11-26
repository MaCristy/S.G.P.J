
import { useEffect, useMemo, useState } from 'react';
import {
    Search,
    ClipboardList,
    GraduationCap,
    BookOpen,
    Eye,
    X,
    RefreshCw,
    UserRound,
    CheckCircle2,
    XCircle,
} from 'lucide-react';

import { apiRequest } from '../services/api.js';

export default function SolicitacoesCadastroPage() {
    const [solicitacoes, setSolicitacoes] = useState([]);
    const [solicitacaoSelecionada, setSolicitacaoSelecionada] = useState(null);

    const [filtro, setFiltro] = useState('Todos');
    const [pesquisa, setPesquisa] = useState('');

    const [loading, setLoading] = useState(true);
    const [processando, setProcessando] = useState(false);
    const [error, setError] = useState('');
    const [mensagem, setMensagem] = useState('');

    const [acao, setAcao] = useState('');
    const [observacao, setObservacao] = useState('');
    const [situacaoAcademica, setSituacaoAcademica] = useState('Ativo');
    const [dataVinculo, setDataVinculo] = useState('');

    // Formata a data recebida do backend para o padrão brasileiro.
    function formatarData(data) {
        if (!data) return 'Não informado';

        const dataFormatada = new Date(data);

        if (Number.isNaN(dataFormatada.getTime())) {
            return 'Não informado';
        }

        return dataFormatada.toLocaleString('pt-BR', {
            dateStyle: 'short',
            timeStyle: 'short',
        });
    }

    // Consulta as solicitações registradas no sistema.
    async function carregarSolicitacoes() {
        try {
            setError('');
            const dados = await apiRequest('/solicitacoes-cadastro/');
            setSolicitacoes(Array.isArray(dados) ? dados : []);
        } catch (erro) {
            setError(erro.message || 'Não foi possível carregar as solicitações.');
        } finally {
            setLoading(false);
        }
    }

    // Carrega a listagem quando a página é aberta.
    useEffect(() => {
        carregarSolicitacoes();
    }, []);

    // Calcula a quantidade de solicitações em cada situação.
    const quantidadePorStatus = useMemo(() => ({
        Todos: solicitacoes.length,
        Pendente: solicitacoes.filter(
            (item) => item.status_solicitacao === 'Pendente'
        ).length,
        Aprovada: solicitacoes.filter(
            (item) => item.status_solicitacao === 'Aprovada'
        ).length,
        Rejeitada: solicitacoes.filter(
            (item) => item.status_solicitacao === 'Rejeitada'
        ).length,
    }), [solicitacoes]);

    // Aplica os filtros de situação e pesquisa.
    const solicitacoesFiltradas = useMemo(() => {
        return solicitacoes.filter((item) => {
            const correspondeStatus =
                filtro === 'Todos' || item.status_solicitacao === filtro;

            const textoPesquisa = pesquisa.toLowerCase();

            const correspondePesquisa = [
                item.nome,
                item.email_institucional,
                item.matricula,
                item.identificacao_funcional,
                item.curso,
            ]
                .filter(Boolean)
                .some((valor) =>
                    String(valor).toLowerCase().includes(textoPesquisa)
                );

            return correspondeStatus && correspondePesquisa;
        });
    }, [solicitacoes, filtro, pesquisa]);

    // Retorna a classe visual correspondente ao status.
    function obterClasseStatus(status) {
        const classes = {
            Pendente: 'pending',
            Aprovada: 'approved',
            Rejeitada: 'rejected',
        };

        return classes[status] || '';
    }

    // Abre a visualização dos dados da solicitação.
    function visualizarSolicitacao(solicitacao) {
        setSolicitacaoSelecionada(solicitacao);
        setAcao('');
        setObservacao('');
        setSituacaoAcademica('Ativo');
        setDataVinculo('');
        setMensagem('');
    }

    // Fecha a janela de detalhes e limpa os campos da análise.
    function fecharDetalhes() {
        if (processando) return;

        setSolicitacaoSelecionada(null);
        setAcao('');
        setObservacao('');
        setMensagem('');
    }

    // Prepara a aprovação ou rejeição da solicitação selecionada.
    function iniciarAnalise(tipo) {
        setAcao(tipo);
        setMensagem('');
        setObservacao('');
        setSituacaoAcademica('Ativo');
        setDataVinculo('');
    }

    // Envia a decisão da Gestão ao backend.
    async function confirmarAnalise(event) {
        event.preventDefault();

        if (!solicitacaoSelecionada || !acao) return;

        if (acao === 'rejeitar' && !observacao.trim()) {
            setMensagem('Informe a justificativa da rejeição.');
            return;
        }

        if (
            acao === 'aprovar' &&
            solicitacaoSelecionada.perfil_solicitado === 'Aluno' &&
            !dataVinculo
        ) {
            setMensagem('Informe a data de vínculo do aluno.');
            return;
        }

        setProcessando(true);
        setMensagem('');

        try {
            const id = solicitacaoSelecionada.id_solicitacao;

            // Monta os dados necessários para cada tipo de decisão.
            const dados = acao === 'aprovar'
                ? {
                    situacao_academica:
                        solicitacaoSelecionada.perfil_solicitado === 'Aluno'
                            ? situacaoAcademica
                            : null,
                    data_vinculo:
                        solicitacaoSelecionada.perfil_solicitado === 'Aluno'
                            ? dataVinculo
                            : null,
                    observacao_analise: observacao.trim() || null,
                }
                : {
                    observacao_analise: observacao.trim(),
                };

            // Envia a decisão para o endpoint correspondente.
            await apiRequest(
                `/solicitacoes-cadastro/${id}/${acao === 'aprovar' ? 'aprovar' : 'rejeitar'}`,
                {
                    method: 'PATCH',
                    body: JSON.stringify(dados),
                }
            );

            // Atualiza a listagem após a confirmação do backend.
            await carregarSolicitacoes();

            setSolicitacaoSelecionada(null);
            setAcao('');
            setObservacao('');
            setMensagem('');
        } catch (erro) {
            setMensagem(
                erro.message || 'Não foi possível concluir a análise.'
            );
        } finally {
            setProcessando(false);
        }
    }

    return (
        <main className="assistidos-page">
            <style>{`
                .campo-legenda {
                display: block;
                color: #667085;
                font-size: 12px;
                margin-bottom: 5px;
                }

                .campo-valor {
                display: block;
                color: #202938;
                font-size: 14px;
                font-weight: 600;
                }

                /* Mantém o rótulo separado do campo e organiza os controles em coluna. */
                .solicitacao-campo {
                    display: flex;
                    flex-direction: column;
                    gap: 7px;
                    color: #202938;
                    font-size: 14px;
                    font-weight: 500;
                }

                .solicitacao-campo select,
                .solicitacao-campo input,
                .solicitacao-campo textarea {
                    display: block;
                    box-sizing: border-box;
                    width: 100%;
                }

                /* Dá espaço e tamanho adequado ao campo de observação. */
                .solicitacao-campo textarea {
                    min-height: 90px;
                    margin-top: 4px;
                    padding: 10px 12px;
                    border: 1px solid #D9DEE8;
                    border-radius: 8px;
                    font: inherit;
                    line-height: 1.5;
                    resize: vertical;
                }

                /* Cria espaço entre o ícone e o texto dos botões de decisão. */
                .solicitacao-botao-acao {
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                }

                .assistidos-page .assistido-modal-actions {
                    gap: 10px;
                    flex-wrap: wrap;
                }
            `}</style>
            <header className="assistidos-heading">
                <div>
                    <span>GESTÃO / COORDENAÇÃO</span>
                    <h1>Solicitações de cadastro</h1>
                    <p>
                        Consulte, aprove ou rejeite solicitações de acesso ao sistema.
                    </p>
                </div>

                <button
                    type="button"
                    className="assistidos-new-button"
                    onClick={() => {
                        setLoading(true);
                        carregarSolicitacoes();
                    }}
                    disabled={loading}
                >
                    <RefreshCw size={17} />
                    Atualizar lista
                </button>
            </header>

            {/* Apresenta a quantidade de solicitações por situação. */}
            <section style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                gap: '14px',
            }}>
                {[
                    { titulo: 'Total', status: 'Todos', cor: '#003874' },
                    { titulo: 'Pendentes', status: 'Pendente', cor: '#A15C00' },
                    { titulo: 'Aprovadas', status: 'Aprovada', cor: '#16803C' },
                    { titulo: 'Rejeitadas', status: 'Rejeitada', cor: '#B42318' },
                ].map((item) => (
                    <article key={item.status} style={{
                        padding: '19px',
                        background: '#FFFFFF',
                        border: '1px solid #D9DEE8',
                        borderRadius: '12px',
                    }}>
                        <span style={{ color: '#667085', fontSize: '12px' }}>
                            {item.titulo}
                        </span>

                        <strong style={{
                            display: 'block',
                            marginTop: '8px',
                            color: item.cor,
                            fontSize: '26px',
                        }}>
                            {quantidadePorStatus[item.status]}
                        </strong>
                    </article>
                ))}
            </section>

            {/* Campo de pesquisa das solicitações. */}
            <section className="assistidos-toolbar">
                <div className="assistidos-search">
                    <Search size={18} />
                    <input
                        type="search"
                        placeholder="Pesquisar por nome, e-mail ou matrícula..."
                        aria-label="Pesquisar solicitações"
                        value={pesquisa}
                        onChange={(event) => setPesquisa(event.target.value)}
                    />
                </div>
            </section>

            {/* Filtros por situação da solicitação. */}
            <section style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '8px',
            }}>
                {['Todos', 'Pendente', 'Aprovada', 'Rejeitada'].map((status) => (
                    <button
                        key={status}
                        type="button"
                        onClick={() => setFiltro(status)}
                        style={{
                            padding: '9px 15px',
                            border: filtro === status
                                ? '1px solid #003874'
                                : '1px solid #D9DEE8',
                            borderRadius: '8px',
                            background: filtro === status ? '#EAF2FB' : '#FFFFFF',
                            color: filtro === status ? '#003874' : '#667085',
                            fontSize: '12px',
                            fontWeight: 600,
                            cursor: 'pointer',
                        }}
                    >
                        {status} ({quantidadePorStatus[status]})
                    </button>
                ))}
            </section>

            {/* Exibe a tabela de solicitações. */}
            <section className="assistidos-table-panel">
                <div className="assistidos-table-heading">
                    <div>
                        <h2>Solicitações registradas</h2>
                        <p>
                            {solicitacoesFiltradas.length} solicitação(ões) encontrada(s).
                        </p>
                    </div>
                    <ClipboardList size={23} />
                </div>

                {loading ? (
                    <div className="assistidos-empty">
                        <RefreshCw size={28} />
                        <p>Carregando solicitações...</p>
                    </div>
                ) : error ? (
                    <div className="assistidos-empty" role="alert">
                        <strong>Não foi possível carregar as solicitações.</strong>
                        <p>{error}</p>
                    </div>
                ) : solicitacoesFiltradas.length === 0 ? (
                    <div className="assistidos-empty">
                        <ClipboardList size={32} />
                        <strong>Nenhuma solicitação encontrada.</strong>
                        <p>
                            Não existem solicitações correspondentes aos filtros selecionados.
                        </p>
                    </div>
                ) : (
                    <div style={{ overflowX: 'auto' }}>
                        <table style={{
                            width: '100%',
                            borderCollapse: 'collapse',
                            textAlign: 'left',
                        }}>
                            <thead>
                                <tr style={{
                                    background: '#F9FAFB',
                                    color: '#667085',
                                    fontSize: '11px',
                                }}>
                                    <th style={{ padding: '14px 18px' }}>Solicitante</th>
                                    <th style={{ padding: '14px 18px' }}>Perfil</th>
                                    <th style={{ padding: '14px 18px' }}>Data</th>
                                    <th style={{ padding: '14px 18px' }}>Situação</th>
                                    <th style={{ padding: '14px 18px' }}>Detalhes</th>
                                </tr>
                            </thead>

                            <tbody>
                                {solicitacoesFiltradas.map((item) => (
                                    <tr key={item.id_solicitacao} style={{
                                        borderTop: '1px solid #EAECF0',
                                        color: '#202938',
                                        fontSize: '12px',
                                    }}>
                                        <td style={{ padding: '16px 18px' }}>
                                            <strong>
                                                {item.nome || `Usuário #${item.id_usuario}`}
                                            </strong>
                                            <small style={{
                                                display: 'block',
                                                marginTop: '5px',
                                                color: '#667085',
                                            }}>
                                                {item.email_institucional || 'E-mail não informado'}
                                            </small>
                                        </td>

                                        <td style={{ padding: '16px 18px' }}>
                                            <span style={{
                                                display: 'inline-flex',
                                                alignItems: 'center',
                                                gap: '6px',
                                            }}>
                                                {item.perfil_solicitado === 'Aluno'
                                                    ? <GraduationCap size={16} />
                                                    : <BookOpen size={16} />}
                                                {item.perfil_solicitado === 'Aluno'
                                                    ? 'Aluno / Estagiário'
                                                    : 'Professor / Orientador'}
                                            </span>
                                        </td>

                                        <td style={{ padding: '16px 18px' }}>
                                            {formatarData(item.data_solicitacao)}
                                        </td>

                                        <td style={{ padding: '16px 18px' }}>
                                            <span className={`solicitacao-status ${obterClasseStatus(item.status_solicitacao)}`}>
                                                {item.status_solicitacao}
                                            </span>
                                        </td>

                                        <td style={{ padding: '16px 18px' }}>
                                            <button
                                                type="button"
                                                onClick={() => visualizarSolicitacao(item)}
                                                style={{
                                                    display: 'inline-flex',
                                                    alignItems: 'center',
                                                    gap: '6px',
                                                    padding: '8px 11px',
                                                    border: '1px solid #D9DEE8',
                                                    borderRadius: '7px',
                                                    background: '#FFFFFF',
                                                    color: '#003874',
                                                    fontSize: '11px',
                                                    fontWeight: 600,
                                                    cursor: 'pointer',
                                                }}
                                            >
                                                <Eye size={15} />
                                                Visualizar
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </section>

            {/* Modal de detalhes e análise da solicitação. */}
            {solicitacaoSelecionada && (
                <div
                    className="assistido-modal-overlay"
                    onClick={fecharDetalhes}
                >
                    <section
                        className="assistido-modal"
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="solicitacao-modal-title"
                        onClick={(event) => event.stopPropagation()}
                    >
                        <header className="assistido-modal-header">
                            <div>
                                <span>ANÁLISE DE CADASTRO</span>
                                <h2 id="solicitacao-modal-title">
                                    Detalhes da solicitação
                                </h2>
                                <p>
                                    Solicitação nº {solicitacaoSelecionada.id_solicitacao}
                                </p>
                            </div>

                            <button
                                type="button"
                                className="assistido-modal-close"
                                onClick={fecharDetalhes}
                                disabled={processando}
                                aria-label="Fechar detalhes"
                            >
                                <X size={21} />
                            </button>
                        </header>

                        <div style={{
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '17px',
                            padding: '22px',
                        }}>
                            <div>
                                <span className="campo-legenda">Nome completo</span>
                                <strong className="campo-valor">
                                    {solicitacaoSelecionada.nome || 'Não informado pela API'}
                                </strong>
                            </div>

                            <div>
                                <span className="campo-legenda">E-mail institucional</span>
                                <strong className="campo-valor">
                                    {solicitacaoSelecionada.email_institucional || 'Não informado pela API'}
                                </strong>
                            </div>

                            <div>
                                <span className="campo-legenda">Perfil solicitado</span>
                                <strong className="campo-valor">
                                    {solicitacaoSelecionada.perfil_solicitado}
                                </strong>
                            </div>

                            {solicitacaoSelecionada.perfil_solicitado === 'Aluno' ? (
                                <>
                                    <div>
                                        <span className="campo-legenda">Matrícula acadêmica</span>
                                        <strong className="campo-valor">
                                            {solicitacaoSelecionada.matricula}
                                        </strong>
                                    </div>

                                    <div>
                                        <span className="campo-legenda">Curso</span>
                                        <strong className="campo-valor">
                                            {solicitacaoSelecionada.curso}
                                        </strong>
                                    </div>

                                    <div>
                                        <span className="campo-legenda">Período</span>
                                        <strong className="campo-valor">
                                            {solicitacaoSelecionada.periodo}
                                        </strong>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <div>
                                        <span className="campo-legenda">Matrícula funcional</span>
                                        <strong className="campo-valor">
                                            {solicitacaoSelecionada.identificacao_funcional}
                                        </strong>
                                    </div>

                                    <div>
                                        <span className="campo-legenda">Área / vínculo</span>
                                        <strong className="campo-valor">
                                            {solicitacaoSelecionada.area_vinculo || 'Não informado'}
                                        </strong>
                                    </div>
                                </>
                            )}

                            <div>
                                <span className="campo-legenda">Data da solicitação</span>
                                <strong className="campo-valor">
                                    {formatarData(solicitacaoSelecionada.data_solicitacao)}
                                </strong>
                            </div>

                            <div>
                                <span className="campo-legenda">Situação atual</span>
                                <strong className="campo-valor">
                                    {solicitacaoSelecionada.status_solicitacao}
                                </strong>
                            </div>

                            {solicitacaoSelecionada.observacao_analise && (
                                <div>
                                    <span className="campo-legenda">Observação da análise</span>
                                    <p style={{ margin: '5px 0 0', lineHeight: 1.6 }}>
                                        {solicitacaoSelecionada.observacao_analise}
                                    </p>
                                </div>
                            )}
                        </div>

                        {/* Exibe os campos necessários para a decisão da Gestão. */}
                        {solicitacaoSelecionada.status_solicitacao === 'Pendente' && (
                            <form onSubmit={confirmarAnalise}>
                                {acao && (
                                    <div style={{
                                        padding: '0 22px 18px',
                                        display: 'flex',
                                        flexDirection: 'column',
                                        gap: '12px',
                                    }}>
                                        {acao === 'aprovar' &&
                                            solicitacaoSelecionada.perfil_solicitado === 'Aluno' && (
                                                <>
                                                    <label className="solicitacao-campo">
                                                        Situação acadêmica
                                                        <select
                                                            value={situacaoAcademica}
                                                            onChange={(event) => setSituacaoAcademica(event.target.value)}
                                                            required
                                                        >
                                                            <option value="Ativo">Ativo</option>
                                                            <option value="Trancado">Trancado</option>
                                                            <option value="Concluído">Concluído</option>
                                                        </select>
                                                    </label>

                                                    <label className="solicitacao-campo">
                                                        Data de vínculo
                                                        <input
                                                            type="date"
                                                            value={dataVinculo}
                                                            onChange={(event) => setDataVinculo(event.target.value)}
                                                            required
                                                        />
                                                    </label>
                                                </>
                                            )}

                                        <label className="solicitacao-campo">
                                            <span>
                                                {acao === 'rejeitar'
                                                    ? 'Justificativa da rejeição'
                                                    : 'Observação da aprovação (opcional)'}
                                            </span>

                                            <textarea
                                                rows="3"
                                                value={observacao}
                                                onChange={(event) => setObservacao(event.target.value)}
                                                placeholder={
                                                    acao === 'rejeitar'
                                                        ? 'Informe o motivo da rejeição...'
                                                        : 'Adicione uma observação, se necessário...'
                                                }
                                                required={acao === 'rejeitar'}
                                            />
                                        </label>
                                    </div>
                                )}

                                {mensagem && (
                                    <p role="alert" style={{
                                        margin: '0 22px 15px',
                                        color: '#B42318',
                                        fontSize: '13px',
                                    }}>
                                        {mensagem}
                                    </p>
                                )}

                                <footer className="assistido-modal-actions">
                                    {!acao ? (
                                        <>
                                            <button
                                                type="button"
                                                className="assistido-cancel-button"
                                                onClick={fecharDetalhes}
                                            >
                                                Fechar
                                            </button>

                                            <button
                                                type="button"
                                                onClick={() => iniciarAnalise('rejeitar')}
                                                className="solicitacao-botao-acao"
                                                style={{
                                                    padding: '10px 15px',
                                                    border: '1px solid #B42318',
                                                    borderRadius: '7px',
                                                    background: '#FFFFFF',
                                                    color: '#B42318',
                                                    cursor: 'pointer',
                                                    fontWeight: 600,
                                                }}
                                            >
                                                <XCircle size={15} />
                                                Rejeitar
                                            </button>

                                            <button
                                                type="button"
                                                onClick={() => iniciarAnalise('aprovar')}
                                                className="solicitacao-botao-acao"
                                                style={{
                                                    padding: '10px 15px',
                                                    border: 'none',
                                                    borderRadius: '7px',
                                                    background: '#16803C',
                                                    color: '#FFFFFF',
                                                    cursor: 'pointer',
                                                    fontWeight: 600,
                                                }}
                                            >
                                                <CheckCircle2 size={15} />
                                                Aprovar
                                            </button>
                                        </>
                                    ) : (
                                        <>
                                            <button
                                                type="button"
                                                className="assistido-cancel-button"
                                                onClick={() => setAcao('')}
                                                disabled={processando}
                                            >
                                                Voltar
                                            </button>

                                            <button
                                                type="submit"
                                                disabled={processando}
                                                style={{
                                                    padding: '10px 17px',
                                                    border: 'none',
                                                    borderRadius: '7px',
                                                    background: acao === 'aprovar' ? '#16803C' : '#B42318',
                                                    color: '#FFFFFF',
                                                    cursor: processando ? 'wait' : 'pointer',
                                                    fontWeight: 600,
                                                }}
                                            >
                                                {processando
                                                    ? 'Processando...'
                                                    : acao === 'aprovar'
                                                        ? 'Confirmar aprovação'
                                                        : 'Confirmar rejeição'}
                                            </button>
                                        </>
                                    )}
                                </footer>
                            </form>
                        )}

                        {/* Solicitações analisadas não podem receber nova decisão. */}
                        {solicitacaoSelecionada.status_solicitacao !== 'Pendente' && (
                            <footer className="assistido-modal-actions">
                                <button
                                    type="button"
                                    className="assistido-cancel-button"
                                    onClick={fecharDetalhes}
                                >
                                    Fechar
                                </button>
                            </footer>
                        )}
                    </section>
                </div>
            )}
        </main>
    );
}
