
from datetime import date, datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)


# Define as situações permitidas para uma atividade.
SituacaoAtividade = Literal[
    "Pendente",
    "Em andamento",
    "Concluída",
    "Cancelada"
]


# Define os campos compartilhados do cadastro de uma atividade.
class AtividadeBase(BaseModel):
    id_caso: int = Field(gt=0)

    titulo: str = Field(
        min_length=1,
        max_length=150
    )

    descricao: str = Field(min_length=1)

    id_responsavel: int = Field(gt=0)

    situacao: SituacaoAtividade = "Pendente"

    prioridade: str = Field(
        default="Média",
        min_length=1,
        max_length=30
    )

    data_prevista: date | None = None


# Define os dados necessários para cadastrar uma atividade.
class AtividadeCreate(AtividadeBase):
    pass


# Define os campos permitidos na atualização de uma atividade.
class AtividadeUpdate(BaseModel):
    id_caso: int | None = Field(default=None, gt=0)

    titulo: str | None = Field(
        default=None,
        min_length=1,
        max_length=150
    )

    descricao: str | None = Field(
        default=None,
        min_length=1
    )

    id_responsavel: int | None = Field(default=None, gt=0)

    situacao: SituacaoAtividade | None = None

    prioridade: str | None = Field(
        default=None,
        min_length=1,
        max_length=30
    )

    data_prevista: date | None = None
    data_conclusao: datetime | None = None

    # Impede valores nulos nos campos obrigatórios do banco.
    @model_validator(mode="before")
    @classmethod
    def validar_campos_obrigatorios(cls, dados):
        campos_obrigatorios = {
            "id_caso",
            "titulo",
            "descricao",
            "id_responsavel",
            "situacao",
            "prioridade"
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


# Define os dados retornados pela API ao consultar uma atividade.
class AtividadeResponse(AtividadeBase):
    model_config = ConfigDict(from_attributes=True)

    id_atividade: int
    data_criacao: datetime
    data_conclusao: datetime | None = None
