
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from pwdlib import PasswordHash

from app.config.settings import settings


# Configura o algoritmo recomendado para geração e verificação de hashes de senhas.
password_hash = PasswordHash.recommended()


# Gera um hash seguro da senha para armazenamento no banco de dados.
def gerar_hash_senha(senha: str) -> str:
    """
    Gera um hash seguro para armazenar a senha do usuário.
    """
    return password_hash.hash(senha)


# Verifica se a senha informada corresponde ao hash armazenado.
def verificar_senha(senha: str, senha_hash: str) -> bool:
    """
    Verifica se a senha informada corresponde ao hash armazenado.
    """
    return password_hash.verify(senha, senha_hash)


# Cria um token JWT contendo os dados necessários para autenticação.
def criar_token_acesso(dados: dict) -> str:
    """
    Gera um token JWT com os dados do usuário.
    """
    # Copia os dados recebidos para evitar modificar o dicionário original.
    dados_token = dados.copy()

    # Define o prazo de validade do token utilizando o horário UTC.
    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Adiciona a data de expiração aos dados do token.
    dados_token.update({"exp": expiracao})

    # Assina e codifica o token utilizando a chave secreta e o algoritmo configurados.
    return jwt.encode(
        dados_token,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


# Valida um token JWT e recupera os dados armazenados em seu conteúdo.
def verificar_token(token: str):
    """
    Valida o token JWT e retorna seus dados.
    """
    try:
        # Decodifica o token e verifica sua assinatura e validade.
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        return payload

    except JWTError:
        # Retorna None quando o token é inválido, expirado ou apresenta erro JWT.
        return None
