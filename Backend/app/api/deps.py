
"""
Dependências compartilhadas da API (FastAPI Dependency Injection).

    - get_db(): Sessão do banco de dados.
    - get_current_user(): Identifica o usuário autenticado.
    - check_role(): Verifica as permissões conforme o perfil.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.usuario import Usuario
from app.core.security import verificar_token


# Define o mecanismo de autenticação por token Bearer.
security = HTTPBearer()


# Identifica e valida o usuário autenticado na requisição.
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    # Prepara a resposta padrão para credenciais inválidas.
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Extrai e valida o token de acesso enviado na requisição.
        token = credentials.credentials
        payload = verificar_token(token)

        # Impede o acesso quando o token não for válido.
        if payload is None:
            raise credenciais_invalidas

        # Obtém o identificador do usuário armazenado no token.
        id_usuario = payload.get("sub")

        if id_usuario is None:
            raise credenciais_invalidas

        # Busca o usuário correspondente no banco de dados.
        usuario = (
            db.query(Usuario)
            .filter(Usuario.id_usuario == int(id_usuario))
            .first()
        )

        # Permite o acesso somente a usuários existentes e ativos.
        if not usuario or usuario.situacao_conta != "Ativo":
            raise credenciais_invalidas

        return usuario

    except (JWTError, ValueError, TypeError):
        # Trata erros de validação ou conversão das credenciais.
        raise credenciais_invalidas


# Cria uma dependência para controlar o acesso conforme o perfil.
def check_role(*perfis_permitidos: str):
    def verificar_perfil(
        usuario: Usuario = Depends(get_current_user)
    ):
        # Verifica se o perfil do usuário está autorizado.
        if usuario.perfil not in perfis_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui permissão para realizar esta operação."
            )

        return usuario

    return verificar_perfil


# Define os recursos disponibilizados pelo módulo.
__all__ = ["get_db", "get_current_user", "check_role"]
