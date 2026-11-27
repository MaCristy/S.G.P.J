
import { apiRequest } from './api.js';

// Lista os prazos disponíveis para o usuário autenticado.
export async function listarPrazos() {
    return apiRequest('/prazos/');
}

// Consulta um prazo específico.
export async function buscarPrazo(idPrazo) {
    return apiRequest(`/prazos/${idPrazo}`);
}

// Lista os prazos vinculados a um caso jurídico.
export async function listarPrazosPorCaso(idCaso) {
    return apiRequest(`/prazos/caso/${idCaso}`);
}

// Lista os prazos atribuídos a um responsável.
export async function listarPrazosPorResponsavel(idResponsavel) {
    return apiRequest(`/prazos/responsavel/${idResponsavel}`);
}

// Cadastra um novo prazo.
export async function criarPrazo(dados) {
    return apiRequest('/prazos/', {
        method: 'POST',
        body: JSON.stringify(dados),
    });
}

// Atualiza um prazo existente.
export async function atualizarPrazo(idPrazo, dados) {
    return apiRequest(`/prazos/${idPrazo}`, {
        method: 'PATCH',
        body: JSON.stringify(dados),
    });
}
