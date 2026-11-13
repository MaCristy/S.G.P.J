

"""
Roteador v1 — agrega todos os routers da versão 1 da API do S.G.P.J.
"""

from fastapi import APIRouter

from app.api.v1.routers import (
    health,
    assistidos,
    atendimentos,
    usuarios,
    casos_juridicos,
    alunos,
    professores,
    atividades,
    documentos,
    prazos,
    historico_caso,
    auth,
)


api_router_v1 = APIRouter()

# Rotas de verificação do sistema.
api_router_v1.include_router(
    health.router,
    tags=["Sistema"],
)

# Módulo de Assistidos.
api_router_v1.include_router(
    assistidos.router,
)

# Módulo de Atendimentos.
api_router_v1.include_router(
    atendimentos.router,
)

# Módulo de Usuários.
api_router_v1.include_router(
    usuarios.router,
)

# Módulo de Casos Jurídicos.
api_router_v1.include_router(
    casos_juridicos.router,
)

# Módulo de Alunos/Estagiários.
api_router_v1.include_router(
    alunos.router,
)

# Módulo de Professores/Orientadores.
api_router_v1.include_router(
    professores.router,
)

# Módulo de Atividades.
api_router_v1.include_router(
    atividades.router,
)

# Módulo de Documentos.
api_router_v1.include_router(
    documentos.router,
)

# Módulo de Prazos.
api_router_v1.include_router(
    prazos.router,
)

# Módulo de Histórico de Casos.
api_router_v1.include_router(
    historico_caso.router,
)

# Módulo de Autenticação.
api_router_v1.include_router(
    auth.router,
)


