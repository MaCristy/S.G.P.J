
import { apiRequest } from './api.js';

// Lista os casos jurídicos disponíveis para o usuário autenticado.
export async function listarCasosJuridicos() {
    return apiRequest('/casos-juridicos/');
}

// Consulta um caso jurídico específico.
export async function buscarCasoJuridico(idCaso) {
    return apiRequest(`/casos-juridicos/${idCaso}`);
}

// Lista os casos vinculados a um assistido.
export async function listarCasosPorAssistido(idAssistido) {
    return apiRequest(`/casos-juridicos/assistido/${idAssistido}`);
}

// Cadastra um novo caso jurídico.
export async function criarCasoJuridico(dados) {
    return apiRequest('/casos-juridicos/', {
        method: 'POST',
        body: JSON.stringify(dados),
    });
}

// Atualiza os dados de um caso jurídico.
export async function atualizarCasoJuridico(idCaso, dados) {
    return apiRequest(`/casos-juridicos/${idCaso}`, {
        method: 'PATCH',
        body: JSON.stringify(dados),
    });
}
