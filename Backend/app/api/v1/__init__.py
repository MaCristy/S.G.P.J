
"""
Roteador v1 — agrega todos os routers da versão 1 da API do S.G.P.J.

Centraliza os módulos da aplicação para que suas rotas sejam
registradas na instância principal do FastAPI.
"""

# Importa o componente responsável por agrupar as rotas
from fastapi import APIRouter


# ============================================================
# 1. IMPORTAÇÃO DOS MÓDULOS
# Reúne os roteadores responsáveis pelas funcionalidades do sistema.
# ============================================================

from app.api.v1.routers import (
    health,                 # Verificação de funcionamento da API
    assistidos,             # Cadastro e gerenciamento de assistidos
    atendimentos,           # Registro e consulta de atendimentos
    usuario as usuarios,    # Gerenciamento de usuários
    casos_juridicos,        # Gerenciamento de casos jurídicos
    aluno as alunos,        # Gerenciamento de alunos
    professor as professores,  # Gerenciamento de professores
    atividade as atividades,   # Gerenciamento de atividades
    documento as documentos,   # Gerenciamento de documentos
    prazo as prazos,        # Gerenciamento de prazos
    historico_caso,         # Consulta do histórico dos casos
    auth,                   # Autenticação e acesso ao sistema
    dashboard               # Indicadores e informações do dashboard
)


# ============================================================
# 2. CRIAÇÃO DO ROTEADOR PRINCIPAL
# Instancia o agrupador que receberá todas as rotas da API v1.
# ============================================================

api_router_v1 = APIRouter()


# ============================================================
# 3. REGISTRO DOS ROTEADORES
# Adiciona cada módulo ao roteador principal da aplicação.
# ============================================================

# Sistema: verifica se a API está funcionando.
api_router_v1.include_router(
    health.router,
    tags=["Sistema"],
)

# Assistidos: gerencia os dados das pessoas atendidas.
api_router_v1.include_router(
    assistidos.router,
)

# Atendimentos: registra e consulta os atendimentos realizados.
api_router_v1.include_router(
    atendimentos.router,
)

# Usuários: gerencia os usuários cadastrados no sistema.
api_router_v1.include_router(
    usuarios.router,
)

# Casos jurídicos: gerencia os casos e suas informações.
api_router_v1.include_router(
    casos_juridicos.router,
)

# Alunos: gerencia os dados dos alunos e estagiários.
api_router_v1.include_router(
    alunos.router,
)

# Professores: gerencia os dados dos professores e orientadores.
api_router_v1.include_router(
    professores.router,
)

# Atividades: controla as atividades vinculadas aos casos.
api_router_v1.include_router(
    atividades.router,
)

# Documentos: gerencia os documentos associados aos casos.
api_router_v1.include_router(
    documentos.router,
)

# Prazos: controla o cadastro e o acompanhamento dos prazos.
api_router_v1.include_router(
    prazos.router,
)

# Histórico: disponibiliza o registro cronológico dos casos.
api_router_v1.include_router(
    historico_caso.router,
)

# Autenticação: disponibiliza as rotas de login e acesso.
api_router_v1.include_router(
    auth.router,
)

# Dashboard: disponibiliza os indicadores de acompanhamento.
api_router_v1.include_router(
    dashboard.router,
)
