
from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    model_validator
)


# Define os dados necessários para cadastrar um usuário.
class UsuarioCreate(BaseModel):
    nome: str = Field(
        min_length=1,
        max_length=150
    )

    email_institucional: EmailStr = Field(
        max_length=150
    )

    senha: str = Field(
        min_length=8,
        max_length=128
    )

    perfil: Literal["Aluno", "Professor", "Gestão"]


# Define os campos permitidos na atualização de um usuário.
class UsuarioUpdate(BaseModel):
    nome: str | None = Field(
        default=None,
        min_length=1,
        max_length=150
    )

    email_institucional: EmailStr | None = Field(
        default=None,
        max_length=150
    )

    senha: str | None = Field(
        default=None,
        min_length=8,
        max_length=128
    )

    perfil: Literal["Aluno", "Professor", "Gestão"] | None = None

    situacao_conta: Literal["Ativo", "Inativo"] | None = None

    # Impede valores nulos quando um campo é enviado na atualização.
    @model_validator(mode="before")
    @classmethod
    def validar_campos_obrigatorios(cls, dados):
        campos_obrigatorios = {
            "nome",
            "email_institucional",
            "senha",
            "perfil",
            "situacao_conta"
        }

        if isinstance(dados, dict):
            campos_nulos = [
                campo
                for campo in campos_obrigatorios
                if campo in dados and dados[campo] is None
            ]

            if campos_nulos:
                raise ValueError(
                    "Os seguintes campos não podem receber null: "
                    f"{', '.join(sorted(campos_nulos))}."
                )

        return dados


# Define os dados retornados pela API ao consultar um usuário.
class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    nome: str
    email_institucional: EmailStr
    perfil: str
    situacao_conta: str
    data_criacao: datetime
    ultimo_acesso: datetime | None = None
