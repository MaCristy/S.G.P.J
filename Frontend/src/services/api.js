
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

// Define a chave utilizada para armazenar o token de autenticação.
export const AUTH_TOKEN_KEY = 'sgpj_token';

// Centraliza as requisições à API, incluindo os cabeçalhos necessários.
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

      // Envia o token para permitir o acesso aos endpoints protegidos.
      ...(token ? { Authorization: `Bearer ${token}` } : {}),

      ...options.headers,
    },
  });

  // Interrompe a execução quando a API retorna uma resposta de erro.
  if (!response.ok) {
    const message = `Erro na comunicação com a API (${response.status}).`;
    throw new Error(message);
  }

  // Retorna null quando a API confirma a operação sem conteúdo.
  if (response.status === 204) return null;

  // Converte a resposta da API para JSON.
  return response.json();
}

export { API_BASE_URL };
