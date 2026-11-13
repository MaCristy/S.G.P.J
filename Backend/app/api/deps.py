"""
Dependências compartilhadas da API (FastAPI Dependency Injection).

Módulo central para injeções reutilizáveis em todos os endpoints:
    - get_db(): Sessão de banco de dados por requisição.
    - get_current_user(): Usuário autenticado a partir do token JWT.
    - check_role(): Verificação de perfil de acesso (RBAC — RN01, RN08).

Atualmente expõe apenas get_db(). As dependências de autenticação
serão adicionadas junto à implementação do módulo de Auth (RF01, RN01).
"""
from app.db.session import get_db

__all__ = ["get_db"]

