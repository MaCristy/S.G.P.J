
"""
Dependências compartilhadas da API (FastAPI Dependency Injection).

    - get_db(): Sessão do banco de dados.
    - get_current_user(): Identifica o usuário autenticado.
    - check_role(): Verifica as permissões conforme o perfil.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.usuario import Usuario
from app.core.security import verificar_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verificar_token(token)

        if payload is None:
            raise credenciais_invalidas

        id_usuario = payload.get("sub")

        if id_usuario is None:
            raise credenciais_invalidas

        usuario = (
            db.query(Usuario)
            .filter(Usuario.id_usuario == int(id_usuario))
            .first()
        )

        if not usuario or usuario.situacao_conta != "Ativo":
            raise credenciais_invalidas

        return usuario

    except (JWTError, ValueError, TypeError):
        raise credenciais_invalidas


def check_role(*perfis_permitidos: str):
    def verificar_perfil(
        usuario: Usuario = Depends(get_current_user)
    ):
        if usuario.perfil not in perfis_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui permissão para realizar esta operação."
            )

        return usuario

    return verificar_perfil


__all__ = ["get_db", "get_current_user", "check_role"]
