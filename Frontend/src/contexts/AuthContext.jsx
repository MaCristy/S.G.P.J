
import {
  createContext,
  useContext,
  useEffect,
  useState
} from 'react';

import {
  apiRequest,
  AUTH_TOKEN_KEY
} from '../services/api.js';

// Gerencia os dados e as operações de autenticação da aplicação.
const AuthContext = createContext(null);

// Extrai o identificador do usuário a partir do token JWT.
function obterIdUsuario(token) {
  try {
    const partes = token.split('.');

    if (partes.length !== 3) {
      throw new Error('Token inválido.');
    }

    // Decodifica o conteúdo do token para obter os dados do usuário.
    const payloadBase64 = partes[1]
      .replace(/-/g, '+')
      .replace(/_/g, '/');

    const payload = JSON.parse(atob(payloadBase64));

    const idUsuario = Number(payload.sub);

    // Verifica se o identificador recebido é válido.
    if (!Number.isInteger(idUsuario) || idUsuario <= 0) {
      throw new Error('Identificador de usuário inválido.');
    }

    return idUsuario;
  } catch {
    throw new Error('Não foi possível identificar o usuário autenticado.');
  }
}

// Consulta os dados cadastrais do usuário autenticado no backend.
async function buscarUsuario(token) {
  const idUsuario = obterIdUsuario(token);

  return apiRequest(`/usuarios/${idUsuario}`);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Restaura a sessão do usuário ao iniciar a aplicação.
  useEffect(() => {
    async function carregarUsuario() {
      const token = localStorage.getItem(AUTH_TOKEN_KEY);

      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const usuario = await buscarUsuario(token);
        setUser(usuario);
      } catch (erro) {
        // Remove o token quando a autenticação não é mais válida.
        if (
          erro.message.includes('(401)') ||
          erro.message.includes('(403)')
        ) {
          localStorage.removeItem(AUTH_TOKEN_KEY);
        }

        setUser(null);
      } finally {
        setLoading(false);
      }
    }

    carregarUsuario();
  }, []);

  // Realiza a autenticação e carrega os dados do usuário.
  async function login(emailInstitucional, senha) {
    setLoading(true);

    try {
      const resposta = await apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          email_institucional: emailInstitucional,
          senha
        })
      });

      if (!resposta.access_token) {
        throw new Error('A API não retornou um token de acesso.');
      }

      // Armazena o token para autenticar as próximas requisições.
      localStorage.setItem(
        AUTH_TOKEN_KEY,
        resposta.access_token
      );

      const usuario = await buscarUsuario(resposta.access_token);

      setUser(usuario);

      return usuario;
    } catch (erro) {
      // Limpa os dados de autenticação caso ocorra alguma falha.
      localStorage.removeItem(AUTH_TOKEN_KEY);
      setUser(null);

      throw erro;
    } finally {
      setLoading(false);
    }
  }

  // Encerra a sessão e remove os dados de autenticação.
  function logout() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    setUser(null);
  }

  const isAuthenticated = Boolean(user);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated,
        login,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// Permite acessar os dados de autenticação nos componentes.
export function useAuth() {
  return useContext(AuthContext);
}
