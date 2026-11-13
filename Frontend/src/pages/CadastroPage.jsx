
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

export default function CadastroPage() {
    const [perfil, setPerfil] = useState('Aluno');
    const [mostrarSenha, setMostrarSenha] = useState(false);
    const [mostrarConfirmacao, setMostrarConfirmacao] = useState(false);

    const [formulario, setFormulario] = useState({
        nome: '',
        email: '',
        matricula: '',
        senha: '',
        confirmarSenha: ''
    });

    const [mensagem, setMensagem] = useState('');

    function atualizarCampo(event) {
        const { name, value } = event.target;

        setFormulario((anterior) => ({
            ...anterior,
            [name]: value
        }));

        setMensagem('');
    }

    function handleSubmit(event) {
        event.preventDefault();

        if (
            !formulario.nome.trim() ||
            !formulario.email.trim() ||
            !formulario.senha ||
            !formulario.confirmarSenha
        ) {
            setMensagem('Preencha todos os campos obrigatórios.');
            return;
        }

        if (perfil === 'Aluno' && !formulario.matricula.trim()) {
            setMensagem('Informe sua matrícula.');
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

        setMensagem(
            'Formulário validado. O cadastro será habilitado após a integração com o servidor.'
        );
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
                    <p>Preencha os dados abaixo para solicitar seu acesso ao S.G.P.J.</p>
                </div>

                <div className="profile-selector">
                    <button
                        type="button"
                        className={`profile-option ${perfil === 'Aluno' ? 'selected' : ''}`}
                        onClick={() => {
                            setPerfil('Aluno');
                            setMensagem('');
                        }}
                    >
                        <GraduationCap size={20} />
                        <span>Aluno / Estagiário</span>
                    </button>

                    <button
                        type="button"
                        className={`profile-option ${perfil === 'Professor' ? 'selected' : ''}`}
                        onClick={() => {
                            setPerfil('Professor');
                            setMensagem('');
                        }}
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
                    />

                    <label htmlFor="cadastro-email">E-mail *</label>
                    <input
                        id="cadastro-email"
                        name="email"
                        type="email"
                        placeholder="Digite seu e-mail"
                        value={formulario.email}
                        onChange={atualizarCampo}
                    />

                    {perfil === 'Aluno' && (
                        <>
                            <label htmlFor="matricula">Matrícula *</label>
                            <input
                                id="matricula"
                                name="matricula"
                                type="text"
                                placeholder="Digite sua matrícula"
                                value={formulario.matricula}
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

                    {perfil === 'Professor' && (
                        <div className="approval-notice">
                            <ShieldCheck size={19} />
                            <p>
                                <strong>Atenção:</strong> o cadastro de Professor / Orientador
                                dependerá da aprovação da Gestão / Coordenação antes da
                                liberação do acesso.
                            </p>
                        </div>
                    )}

                    {mensagem && (
                        <p className="auth-message" role="status">
                            {mensagem}
                        </p>
                    )}

                    <button type="submit" className="auth-submit">
                        Solicitar cadastro
                    </button>
                </form>

                <p className="auth-register">
                    Já possui uma conta? <Link to="/login">Faça login</Link>
                </p>

                <div className="auth-security">
                    <ShieldCheck size={17} />
                    <span>Seus dados serão tratados conforme as permissões do sistema</span>
                </div>
            </div>
        </section>
    );
}
