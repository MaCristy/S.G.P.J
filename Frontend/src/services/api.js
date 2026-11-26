
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

// Define a chave utilizada para armazenar o token de autenticação.
export const AUTH_TOKEN_KEY = 'sgpj_token';

// Centraliza as requisições à API e trata as respostas de sucesso e erro.
export async function apiRequest(path, options = {}) {
  // Recupera o token de autenticação armazenado após o login.
  const token = localStorage.getItem(AUTH_TOKEN_KEY);

  // Monta e executa a requisição, incluindo o token quando disponível.
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      Accept: 'application/json',

      // Define o formato JSON, exceto quando o conteúdo é enviado como arquivo.
      ...(options.body && !(options.body instanceof FormData)
        ? { 'Content-Type': 'application/json' }
        : {}),

      // Envia o token somente quando existe uma sessão autenticada.
      ...(token ? { Authorization: `Bearer ${token}` } : {}),

      ...options.headers,
    },
  });

  // Retorna null quando a API confirma a operação sem conteúdo.
  if (response.status === 204) {
    return null;
  }

  // Lê a resposta para identificar mensagens específicas do backend.
  const textoResposta = await response.text();

  let dadosResposta = null;

  try {
    dadosResposta = textoResposta ? JSON.parse(textoResposta) : null;
  } catch {
    dadosResposta = null;
  }

  // Apresenta o motivo real quando a API retorna um erro.
  if (!response.ok) {
    let mensagem = `Erro na comunicação com a API (${response.status}).`;

    if (typeof dadosResposta?.detail === 'string') {
      mensagem = dadosResposta.detail;
    } else if (Array.isArray(dadosResposta?.detail)) {
      mensagem = dadosResposta.detail
        .map((erro) => {
          const campo = Array.isArray(erro.loc)
            ? erro.loc.filter((parte) => parte !== 'body').join('.')
            : '';

          return campo
            ? `${campo}: ${erro.msg}`
            : erro.msg;
        })
        .join(' | ');
    } else if (typeof dadosResposta?.message === 'string') {
      mensagem = dadosResposta.message;
    }

    throw new Error(mensagem);
  }

  // Retorna os dados recebidos da API.
  return dadosResposta;
}

export { API_BASE_URL };
