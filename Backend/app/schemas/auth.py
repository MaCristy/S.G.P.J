from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email_institucional: EmailStr
    senha: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    id_usuario: int | None = None
    perfil: str | None = None