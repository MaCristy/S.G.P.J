
import { apiRequest } from './api.js';

// Lista as atividades disponíveis para o usuário autenticado.
export async function listarAtividades() {
    return apiRequest('/atividades/');
}

// Consulta uma atividade específica.
export async function buscarAtividade(idAtividade) {
    return apiRequest(`/atividades/${idAtividade}`);
}

// Lista as atividades vinculadas a um caso jurídico.
export async function listarAtividadesPorCaso(idCaso) {
    return apiRequest(`/atividades/caso/${idCaso}`);
}

// Lista as atividades atribuídas a um responsável.
export async function listarAtividadesPorResponsavel(idResponsavel) {
    return apiRequest(`/atividades/responsavel/${idResponsavel}`);
}

// Cadastra uma nova atividade.
export async function criarAtividade(dados) {
    return apiRequest('/atividades/', {
        method: 'POST',
        body: JSON.stringify(dados),
    });
}

// Atualiza uma atividade existente.
export async function atualizarAtividade(idAtividade, dados) {
    return apiRequest(`/atividades/${idAtividade}`, {
        method: 'PATCH',
        body: JSON.stringify(dados),
    });
}
