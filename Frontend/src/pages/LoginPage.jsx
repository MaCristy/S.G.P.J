
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, ShieldCheck } from 'lucide-react';

import { useAuth } from '../contexts/AuthContext.jsx';

export default function LoginPage() {
    const navigate = useNavigate();
    const { login, loading } = useAuth();

    const [showPassword, setShowPassword] = useState(false);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');

    // Valida os dados informados e realiza a autenticação do usuário.
    async function handleSubmit(event) {
        event.preventDefault();
        setMessage('');

        // Impede o envio quando os campos obrigatórios não estão preenchidos.
        if (!email.trim() || !password) {
            setMessage('Preencha todos os campos para continuar.');
            return;
        }

        try {
            // Envia as credenciais ao backend e recupera os dados do usuário.
            const usuario = await login(email.trim(), password);

            // Redireciona o usuário conforme o perfil autenticado.
            if (usuario.perfil === 'Gestão') {
                navigate('/cadastro');
                return;
            }

            if (usuario.perfil === 'Aluno') {
                navigate('/dashboard/aluno');
                return;
            }

            // Informa quando o painel do perfil autenticado ainda não está disponível.
            setMessage(
                `Login realizado, mas o painel para o perfil ${usuario.perfil} ainda não está disponível.`
            );
        } catch (erro) {
            // Identifica erros de autenticação relacionados a credenciais inválidas.
            if (erro.message.includes('(401)')) {
                setMessage('E-mail ou senha inválidos.');
                return;
            }

            // Apresenta uma mensagem para os demais erros de comunicação ou autenticação.
            setMessage(
                erro.message || 'Não foi possível realizar o login. Tente novamente.'
            );
        }
    }

    return (
        <section className="auth-page">
            <div className="auth-card">
                <div className="auth-heading">
                    <span className="auth-symbol">§</span>
                    <span className="auth-eyebrow">SISTEMA DE GESTÃO</span>
                    <h1>Bem-vindo de volta!</h1>
                    <p>Entre com suas credenciais para acessar o S.G.P.J.</p>
                </div>

                <form onSubmit={handleSubmit} className="auth-form">
                    <label htmlFor="email">E-mail</label>
                    <input
                        id="email"
                        type="email"
                        placeholder="Digite seu e-mail"
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                        required
                    />

                    <label htmlFor="password">Senha</label>
                    <div className="password-field">
                        <input
                            id="password"
                            type={showPassword ? 'text' : 'password'}
                            placeholder="Digite sua senha"
                            value={password}
                            onChange={(event) => setPassword(event.target.value)}
                            required
                        />

                        <button
                            type="button"
                            className="password-toggle"
                            onClick={() => setShowPassword(!showPassword)}
                            aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
                        >
                            {showPassword ? <EyeOff size={19} /> : <Eye size={19} />}
                        </button>
                    </div>

                    <div className="forgot-password">
                        <Link to="/recuperar-senha">
                            Esqueci minha senha
                        </Link>
                    </div>

                    {message && (
                        <p className="auth-message" role="status">
                            {message}
                        </p>
                    )}

                    <button
                        type="submit"
                        className="auth-submit"
                        disabled={loading}
                    >
                        {loading ? 'Entrando...' : 'Entrar'}
                    </button>
                </form>

                <p className="auth-register">
                    Ainda não possui cadastro? <Link to="/cadastro">Cadastre-se</Link>
                </p>

                <div className="auth-security">
                    <ShieldCheck size={17} />
                    <span>Ambiente de acesso institucional</span>
                </div>
            </div>
        </section>
    );
}
