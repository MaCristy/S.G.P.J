
import { apiRequest, API_BASE_URL, AUTH_TOKEN_KEY } from './api.js';

// Lista os documentos disponíveis para o usuário autenticado.
export async function listarDocumentos() {
    return apiRequest('/documentos/');
}

// Lista os documentos vinculados a um caso jurídico.
export async function listarDocumentosPorCaso(idCaso) {
    return apiRequest(`/documentos/caso/${idCaso}`);
}

// Lista os documentos vinculados a um atendimento.
export async function listarDocumentosPorAtendimento(idAtendimento) {
    return apiRequest(`/documentos/atendimento/${idAtendimento}`);
}

// Envia um arquivo PDF vinculado a um caso ou atendimento.
export async function enviarDocumento({
    arquivo,
    idCaso = null,
    idAtendimento = null,
    classificacaoAcesso = null
}) {
    const formulario = new FormData();

    formulario.append('arquivo', arquivo);

    if (idCaso !== null) {
        formulario.append('id_caso', idCaso);
    }

    if (idAtendimento !== null) {
        formulario.append('id_atendimento', idAtendimento);
    }

    if (classificacaoAcesso) {
        formulario.append('classificacao_acesso', classificacaoAcesso);
    }

    return apiRequest('/documentos/upload', {
        method: 'POST',
        body: formulario
    });
}

// Baixa o arquivo PDF, mantendo a autenticação do usuário.
export async function baixarDocumento(idDocumento) {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);

    const resposta = await fetch(
        `${API_BASE_URL}/documentos/${idDocumento}/arquivo`,
        {
            headers: {
                ...(token ? { Authorization: `Bearer ${token}` } : {})
            }
        }
    );

    if (!resposta.ok) {
        let mensagem = 'Não foi possível baixar o documento.';

        try {
            const erro = await resposta.json();

            if (typeof erro.detail === 'string') {
                mensagem = erro.detail;
            }
        } catch {
            // Mantém a mensagem padrão se a resposta não for JSON.
        }

        throw new Error(mensagem);
    }

    return resposta.blob();
}
