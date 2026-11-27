
import { apiRequest } from './api.js';

// Lista os registros históricos disponíveis para o usuário autenticado.
export async function listarHistorico() {
    return apiRequest('/historico-casos/');
}

// Lista os registros históricos vinculados a um caso específico.
export async function listarHistoricoPorCaso(idCaso) {
    return apiRequest(`/historico-casos/caso/${idCaso}`);
}

// Consulta um registro histórico específico.
export async function buscarHistorico(idHistorico) {
    return apiRequest(`/historico-casos/${idHistorico}`);
}
