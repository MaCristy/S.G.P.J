
import { apiRequest } from './api.js';

// Lista as notificações do usuário autenticado.
export async function listarNotificacoes() {
    return apiRequest('/notificacoes/');
}

// Consulta a quantidade de notificações não lidas.
export async function contarNotificacoesNaoLidas() {
    return apiRequest('/notificacoes/nao-lidas');
}

// Marca uma notificação específica como lida.
export async function marcarNotificacaoComoLida(idNotificacao) {
    return apiRequest(`/notificacoes/${idNotificacao}/lida`, {
        method: 'PATCH',
    });
}
