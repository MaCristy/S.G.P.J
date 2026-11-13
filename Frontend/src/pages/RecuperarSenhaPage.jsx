
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Mail, ShieldCheck } from 'lucide-react';

export default function RecuperarSenhaPage() {
    const [email, setEmail] = useState('');
    const [mensagem, setMensagem] = useState('');

    function handleSubmit(event) {
        event.preventDefault();

        if (!email.trim()) {
            setMensagem('Informe seu e-mail para continuar.');
            return;
        }

        setMensagem(
            'Solicitação validada visualmente. O envio do link será habilitado após a integração com o servidor.'
        );
    }

    return (
        <section className="auth-page">
            <div className="auth-card">
                <Link to="/login" className="back-link">
                    <ArrowLeft size={16} />
                    Voltar para o login
                </Link>

                <div className="auth-heading">
                    <span className="auth-symbol">
                        <Mail size={29} />
                    </span>
                    <span className="auth-eyebrow">RECUPERAÇÃO DE ACESSO</span>
                    <h1>Esqueceu sua senha?</h1>
                    <p>
                        Informe o e-mail cadastrado no sistema para solicitar
                        a recuperação da sua senha.
                    </p>
                </div>

                <form className="auth-form" onSubmit={handleSubmit}>
                    <label htmlFor="email-recuperacao">E-mail cadastrado</label>

                    <input
                        id="email-recuperacao"
                        type="email"
                        placeholder="Digite seu e-mail"
                        value={email}
                        onChange={(event) => {
                            setEmail(event.target.value);
                            setMensagem('');
                        }}
                    />

                    {mensagem && (
                        <p className="auth-message" role="status">
                            {mensagem}
                        </p>
                    )}

                    <button type="submit" className="auth-submit">
                        Solicitar recuperação
                    </button>
                </form>

                <div className="auth-security">
                    <ShieldCheck size={17} />
                    <span>Recuperação de acesso institucional</span>
                </div>
            </div>
        </section>
    );
}
