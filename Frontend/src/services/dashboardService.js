import { apiRequest } from './api.js';

// Busca os indicadores e as informações da visão geral do Aluno.
export async function buscarDashboardAluno() {
    return apiRequest('/dashboard/aluno');
}

// Busca os indicadores e as informações da visão geral do Professor.
export async function buscarDashboardProfessor() {
    return apiRequest('/dashboard/professor');
}