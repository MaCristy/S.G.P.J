
const API_URL = 'http://127.0.0.1:8000/api/v1/assistidos/';

async function tratarResposta(response) {
    const dados = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(
            dados.detail || 'Não foi possível realizar a operação.'
        );
    }

    return dados;
}

// Listar todos os assistidos
export async function listarAssistidos() {
    const response = await fetch(API_URL);
    return tratarResposta(response);
}

// Cadastrar um novo assistido
export async function criarAssistido(dados) {
    const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(dados),
    });

    return tratarResposta(response);
}

// Atualizar um assistido existente
export async function atualizarAssistido(id, dados) {
    const response = await fetch(`${API_URL}${id}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(dados),
    });

    return tratarResposta(response);
}
