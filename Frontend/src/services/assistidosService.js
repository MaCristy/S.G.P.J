
import { apiRequest } from './api.js';

// Listar todos os assistidos
export async function listarAssistidos() {
    return apiRequest('/assistidos/');
}

// Cadastrar um novo assistido
export async function criarAssistido(dados) {
    return apiRequest('/assistidos/', {
        method: 'POST',
        body: JSON.stringify(dados),
    });
}

// Atualizar um assistido existente
export async function atualizarAssistido(id, dados) {
    return apiRequest(`/assistidos/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(dados),
    });
}
