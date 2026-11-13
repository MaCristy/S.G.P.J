
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from pwdlib import PasswordHash

from app.config.settings import settings


# Configuração do algoritmo de hash de senhas
password_hash = PasswordHash.recommended()


def gerar_hash_senha(senha: str) -> str:
    """
    Gera um hash seguro para armazenar a senha do usuário.
    """
    return password_hash.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """
    Verifica se a senha informada corresponde ao hash armazenado.
    """
    return password_hash.verify(senha, senha_hash)


def criar_token_acesso(dados: dict) -> str:
    """
    Gera um token JWT com os dados do usuário.
    """
    dados_token = dados.copy()

    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    dados_token.update({"exp": expiracao})

    return jwt.encode(
        dados_token,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def verificar_token(token: str):
    """
    Valida o token JWT e retorna seus dados.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        return payload

    except JWTError:
        return None
