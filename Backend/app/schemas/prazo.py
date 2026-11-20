
from datetime import date, datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)


# Define as situações permitidas para um prazo.
SituacaoPrazo = Literal[
    "Pendente de validação",
    "Pendente",
    "Concluído",
    "Vencido",
    "Rejeitado"
]


# Define os dados necessários para cadastrar um prazo.
class PrazoCreate(BaseModel):
    id_caso: int = Field(gt=0)
    id_atividade: int | None = Field(default=None, gt=0)

    descricao: str = Field(
        min_length=1,
        max_length=255
    )

    data_limite: date

    situacao: SituacaoPrazo = "Pendente"

    id_responsavel: int = Field(gt=0)
    observacoes: str | None = None


# Define os campos permitidos na atualização de um prazo.
class PrazoUpdate(BaseModel):
    id_caso: int | None = Field(default=None, gt=0)
    id_atividade: int | None = Field(default=None, gt=0)

    descricao: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )

    data_limite: date | None = None

    situacao: SituacaoPrazo | None = None

    id_responsavel: int | None = Field(default=None, gt=0)
    observacoes: str | None = None
    motivo_rejeicao: str | None = None

    # Impede valores nulos nos campos obrigatórios do banco.
    @model_validator(mode="before")
    @classmethod
    def validar_campos_obrigatorios(cls, dados):
        campos_obrigatorios = {
            "id_caso",
            "descricao",
            "data_limite",
            "situacao",
            "id_responsavel"
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


# Define os dados retornados pela API ao consultar um prazo.
class PrazoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_prazo: int
    id_caso: int
    id_atividade: int | None
    descricao: str
    data_limite: date
    situacao: str
    id_responsavel: int
    observacoes: str | None
    data_conclusao: datetime | None
    motivo_rejeicao: str | None
