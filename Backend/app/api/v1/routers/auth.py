
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import autenticar_usuario


# Configuração das rotas de autenticação.
router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)


# Realiza a autenticação do usuário e retorna o token de acesso.
@router.post("/login", response_model=TokenResponse)
def login(
    # Recebe o e-mail institucional e a senha informados no login.
    dados: LoginRequest,

    # Obtém a conexão com o banco de dados.
    db: Session = Depends(get_db)
):
    # Encaminha as credenciais para o serviço de autenticação.
    resultado = autenticar_usuario(
        db=db,
        email_institucional=dados.email_institucional,
        senha=dados.senha
    )

    # Retorna erro caso as credenciais sejam inválidas.
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos."
        )

    # Retorna os dados de autenticação, incluindo o token.
    return resultado
