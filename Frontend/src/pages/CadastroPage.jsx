
import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
    ArrowLeft,
    Eye,
    EyeOff,
    GraduationCap,
    BookOpen,
    ShieldCheck
} from 'lucide-react';

import { apiRequest } from '../services/api.js';

export default function CadastroPage() {
    const [perfil, setPerfil] = useState('Aluno');
    const [mostrarSenha, setMostrarSenha] = useState(false);
    const [mostrarConfirmacao, setMostrarConfirmacao] = useState(false);
    const [enviando, setEnviando] = useState(false);
    const [sucesso, setSucesso] = useState(false);

    const [formulario, setFormulario] = useState({
        nome: '',
        email: '',
        matricula: '',
        curso: '',
        periodo: '',
        identificacaoFuncional: '',
        areaVinculo: '',
        senha: '',
        confirmarSenha: ''
    });

    const [mensagem, setMensagem] = useState('');

    // Atualiza os campos do formulário conforme o usuário digita.
    function atualizarCampo(event) {
        const { name, value } = event.target;

        setFormulario((anterior) => ({
            ...anterior,
            [name]: value
        }));

        setMensagem('');
        setSucesso(false);
    }

    // Alterna o perfil e limpa os campos específicos do perfil anterior.
    function selecionarPerfil(novoPerfil) {
        setPerfil(novoPerfil);
        setMensagem('');
        setSucesso(false);

        setFormulario((anterior) => ({
            ...anterior,
            matricula: '',
            curso: '',
            periodo: '',
            identificacaoFuncional: '',
            areaVinculo: ''
        }));
    }

    // Valida os dados e envia a solicitação de cadastro ao backend.
    async function handleSubmit(event) {
        event.preventDefault();

        setMensagem('');
        setSucesso(false);

        if (
            !formulario.nome.trim() ||
            !formulario.email.trim() ||
            !formulario.senha ||
            !formulario.confirmarSenha
        ) {
            setMensagem('Preencha todos os campos obrigatórios.');
            return;
        }

        if (perfil === 'Aluno') {
            if (
                !formulario.matricula.trim() ||
                !formulario.curso.trim() ||
                !formulario.periodo
            ) {
                setMensagem('Informe sua matrícula, curso e período atual.');
                return;
            }

            if (
                !Number.isInteger(Number(formulario.periodo)) ||
                Number(formulario.periodo) < 1
            ) {
                setMensagem('Informe um período válido.');
                return;
            }
        }

        if (
            perfil === 'Professor' &&
            !formulario.identificacaoFuncional.trim()
        ) {
            setMensagem('Informe sua matrícula funcional.');
            return;
        }

        if (formulario.senha.length < 8) {
            setMensagem('A senha deve possuir pelo menos 8 caracteres.');
            return;
        }

        if (formulario.senha !== formulario.confirmarSenha) {
            setMensagem('As senhas informadas não coincidem.');
            return;
        }

        // Organiza os dados conforme o perfil selecionado.
        const dadosCadastro = {
            nome: formulario.nome.trim(),
            email_institucional: formulario.email.trim(),
            senha: formulario.senha,
            confirmar_senha: formulario.confirmarSenha,
            perfil_solicitado: perfil,

            matricula: perfil === 'Aluno'
                ? formulario.matricula.trim()
                : null,

            curso: perfil === 'Aluno'
                ? formulario.curso.trim()
                : null,

            periodo: perfil === 'Aluno'
                ? Number(formulario.periodo)
                : null,

            identificacao_funcional: perfil === 'Professor'
                ? formulario.identificacaoFuncional.trim()
                : null,

            area_vinculo: perfil === 'Professor'
                ? formulario.areaVinculo.trim() || null
                : null
        };

        try {
            setEnviando(true);

            // Envia a solicitação para o endpoint público de cadastro.
            await apiRequest('/solicitacoes-cadastro/', {
                method: 'POST',
                body: JSON.stringify(dadosCadastro)
            });

            setSucesso(true);
            setMensagem(
                'Solicitação enviada com sucesso! Seu cadastro está pendente de análise pela Gestão / Coordenação. O acesso será liberado após a aprovação.'
            );

            // Limpa os campos após o envio confirmado pela API.
            setFormulario({
                nome: '',
                email: '',
                matricula: '',
                curso: '',
                periodo: '',
                identificacaoFuncional: '',
                areaVinculo: '',
                senha: '',
                confirmarSenha: ''
            });
        } catch (erro) {
            // Apresenta a falha sem indicar que a solicitação foi concluída.
            setMensagem(
                erro.message || 'Não foi possível enviar sua solicitação. Tente novamente.'
            );
        } finally {
            setEnviando(false);
        }
    }

    return (
        <section className="auth-page cadastro-page">
            <div className="auth-card cadastro-card">
                <Link to="/login" className="back-link">
                    <ArrowLeft size={16} />
                    Voltar para o login
                </Link>

                <div className="auth-heading">
                    <span className="auth-symbol">§</span>
                    <span className="auth-eyebrow">NOVO USUÁRIO</span>
                    <h1>Crie sua conta</h1>
                    <p>
                        Preencha os dados abaixo para solicitar seu acesso ao S.G.P.J.
                    </p>
                </div>

                <div className="profile-selector">
                    <button
                        type="button"
                        className={`profile-option ${perfil === 'Aluno' ? 'selected' : ''}`}
                        onClick={() => selecionarPerfil('Aluno')}
                        disabled={enviando}
                    >
                        <GraduationCap size={20} />
                        <span>Aluno / Estagiário</span>
                    </button>

                    <button
                        type="button"
                        className={`profile-option ${perfil === 'Professor' ? 'selected' : ''}`}
                        onClick={() => selecionarPerfil('Professor')}
                        disabled={enviando}
                    >
                        <BookOpen size={20} />
                        <span>Professor / Orientador</span>
                    </button>
                </div>

                <form className="auth-form" onSubmit={handleSubmit}>
                    <label htmlFor="nome">Nome completo *</label>
                    <input
                        id="nome"
                        name="nome"
                        type="text"
                        placeholder="Digite seu nome completo"
                        value={formulario.nome}
                        onChange={atualizarCampo}
                        required
                    />

                    <label htmlFor="cadastro-email">E-mail institucional *</label>
                    <input
                        id="cadastro-email"
                        name="email"
                        type="email"
                        placeholder="Digite seu e-mail institucional"
                        value={formulario.email}
                        onChange={atualizarCampo}
                        required
                    />

                    {perfil === 'Aluno' && (
                        <>
                            <label htmlFor="matricula">Matrícula acadêmica *</label>
                            <input
                                id="matricula"
                                name="matricula"
                                type="text"
                                placeholder="Digite sua matrícula"
                                value={formulario.matricula}
                                onChange={atualizarCampo}
                                required
                            />

                            <label htmlFor="curso">Curso *</label>
                            <input
                                id="curso"
                                name="curso"
                                type="text"
                                placeholder="Digite seu curso"
                                value={formulario.curso}
                                onChange={atualizarCampo}
                                required
                            />

                            <label htmlFor="periodo">Período atual *</label>
                            <input
                                id="periodo"
                                name="periodo"
                                type="number"
                                min="1"
                                step="1"
                                placeholder="Ex.: 5"
                                value={formulario.periodo}
                                onChange={atualizarCampo}
                                required
                            />
                        </>
                    )}

                    {perfil === 'Professor' && (
                        <>
                            <label htmlFor="identificacaoFuncional">
                                Matrícula funcional *
                            </label>
                            <input
                                id="identificacaoFuncional"
                                name="identificacaoFuncional"
                                type="text"
                                placeholder="Digite sua matrícula funcional"
                                value={formulario.identificacaoFuncional}
                                onChange={atualizarCampo}
                                required
                            />

                            <label htmlFor="areaVinculo">
                                Área / vínculo (opcional)
                            </label>
                            <input
                                id="areaVinculo"
                                name="areaVinculo"
                                type="text"
                                placeholder="Ex.: Direito Civil"
                                value={formulario.areaVinculo}
                                onChange={atualizarCampo}
                            />
                        </>
                    )}

                    <label htmlFor="cadastro-senha">Senha *</label>
                    <div className="password-field">
                        <input
                            id="cadastro-senha"
                            name="senha"
                            type={mostrarSenha ? 'text' : 'password'}
                            placeholder="Mínimo de 8 caracteres"
                            value={formulario.senha}
                            onChange={atualizarCampo}
                            required
                        />

                        <button
                            type="button"
                            className="password-toggle"
                            onClick={() => setMostrarSenha(!mostrarSenha)}
                            aria-label={mostrarSenha ? 'Ocultar senha' : 'Mostrar senha'}
                        >
                            {mostrarSenha ? <EyeOff size={19} /> : <Eye size={19} />}
                        </button>
                    </div>

                    <label htmlFor="confirmar-senha">Confirmar senha *</label>
                    <div className="password-field">
                        <input
                            id="confirmar-senha"
                            name="confirmarSenha"
                            type={mostrarConfirmacao ? 'text' : 'password'}
                            placeholder="Digite novamente sua senha"
                            value={formulario.confirmarSenha}
                            onChange={atualizarCampo}
                            required
                        />

                        <button
                            type="button"
                            className="password-toggle"
                            onClick={() => setMostrarConfirmacao(!mostrarConfirmacao)}
                            aria-label={
                                mostrarConfirmacao ? 'Ocultar senha' : 'Mostrar senha'
                            }
                        >
                            {mostrarConfirmacao
                                ? <EyeOff size={19} />
                                : <Eye size={19} />}
                        </button>
                    </div>

                    <div className="approval-notice">
                        <ShieldCheck size={19} />
                        <p>
                            <strong>Atenção:</strong> sua solicitação será analisada
                            pela Gestão / Coordenação. O acesso ao sistema somente
                            será liberado após a aprovação.
                        </p>
                    </div>

                    {mensagem && (
                        <p
                            className="auth-message"
                            role="status"
                            aria-live="polite"
                        >
                            {mensagem}
                        </p>
                    )}

                    <button
                        type="submit"
                        className="auth-submit"
                        disabled={enviando}
                    >
                        {enviando
                            ? 'Enviando solicitação...'
                            : 'Solicitar cadastro'}
                    </button>
                </form>

                <p className="auth-register">
                    Já possui uma conta? <Link to="/login">Faça login</Link>
                </p>

                <div className="auth-security">
                    <ShieldCheck size={17} />
                    <span>
                        Seus dados serão tratados conforme as permissões do sistema
                    </span>
                </div>
            </div>
        </section>
    );
}
