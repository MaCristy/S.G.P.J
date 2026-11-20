
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)


# Define os campos compartilhados do cadastro de um assistido.
class AssistidoBase(BaseModel):
    nome_completo: str = Field(
        min_length=1,
        max_length=200
    )

    identificador_cadastral: str = Field(
        min_length=1,
        max_length=50
    )

    contato: str = Field(
        min_length=1,
        max_length=100
    )

    endereco: str | None = None
    observacoes_administrativas: str | None = None


# Define os dados necessários para cadastrar um assistido.
class AssistidoCreate(AssistidoBase):
    situacao: str = Field(
        default="Ativo",
        min_length=1,
        max_length=30
    )


# Define os campos permitidos na atualização de um assistido.
class AssistidoUpdate(BaseModel):
    nome_completo: str | None = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    identificador_cadastral: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    contato: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    endereco: str | None = None
    observacoes_administrativas: str | None = None

    situacao: str | None = Field(
        default=None,
        min_length=1,
        max_length=30
    )

    # Impede valores nulos nos campos obrigatórios do banco.
    @model_validator(mode="before")
    @classmethod
    def validar_campos_obrigatorios(cls, dados):
        campos_obrigatorios = {
            "nome_completo",
            "identificador_cadastral",
            "contato",
            "situacao"
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


# Define os dados retornados pela API ao consultar um assistido.
class AssistidoResponse(AssistidoBase):
    model_config = ConfigDict(from_attributes=True)

    id_assistido: int
    data_cadastro: datetime
    situacao: str
