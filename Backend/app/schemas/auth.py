
from pydantic import BaseModel, EmailStr, Field


# Define os dados recebidos para realizar a autenticação.
class LoginRequest(BaseModel):
    email_institucional: EmailStr
    senha: str = Field(min_length=1)


# Define o formato do token retornado após a autenticação.
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Representa os dados do usuário armazenados no token.
class TokenData(BaseModel):
    id_usuario: int | None = None
    perfil: str | None = None
