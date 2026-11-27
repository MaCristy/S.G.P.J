
import { apiRequest } from './api.js';

// Busca os atendimentos que o usuário autenticado tem permissão para consultar.
export async function listarAtendimentos() {
    return apiRequest('/atendimentos/');
}

// Busca os atendimentos vinculados a um assistido específico.
export async function listarAtendimentosPorAssistido(idAssistido) {
    return apiRequest(`/atendimentos/assistido/${idAssistido}`);
}

// Registra um atendimento e envia os dados para o backend.
export async function criarAtendimento(dados) {
    return apiRequest('/atendimentos/', {
        method: 'POST',
        body: JSON.stringify(dados),
    });
}
