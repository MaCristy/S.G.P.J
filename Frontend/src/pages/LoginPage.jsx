
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Eye, EyeOff, ShieldCheck } from 'lucide-react';

export default function LoginPage() {
    const [showPassword, setShowPassword] = useState(false);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');

    function handleSubmit(event) {
        event.preventDefault();

        if (!email.trim() || !password) {
            setMessage('Preencha todos os campos para continuar.');
            return;
        }

        setMessage(
            'A autenticação será habilitada após a integração com o servidor.'
        );
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
                    />

                    <label htmlFor="password">Senha</label>
                    <div className="password-field">
                        <input
                            id="password"
                            type={showPassword ? 'text' : 'password'}
                            placeholder="Digite sua senha"
                            value={password}
                            onChange={(event) => setPassword(event.target.value)}
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
                        <p className="auth-message" role="status">{message}</p>
                    )}

                    <button type="submit" className="auth-submit">
                        Entrar
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
