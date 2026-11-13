
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=150)
    email_institucional: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    perfil: str = Field(min_length=1, max_length=50)


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    nome: str
    email_institucional: EmailStr
    perfil: str
    situacao_conta: str
    data_criacao: datetime
    ultimo_acesso: datetime | None = None
