
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


SituacaoAtividade = Literal[
    "Pendente",
    "Em andamento",
    "Concluída",
    "Cancelada"
]


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


class AtividadeCreate(AtividadeBase):
    pass


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


class AtividadeResponse(AtividadeBase):

    model_config = ConfigDict(from_attributes=True)

    id_atividade: int

    data_criacao: datetime

    data_conclusao: datetime | None = None
