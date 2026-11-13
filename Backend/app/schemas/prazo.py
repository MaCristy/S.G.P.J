
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PrazoCreate(BaseModel):
    id_caso: int
    id_atividade: int | None = None

    descricao: str = Field(min_length=1, max_length=255)
    data_limite: date

    situacao: Literal[
        "Pendente",
        "Concluído",
        "Vencido"
    ] = "Pendente"

    id_responsavel: int
    observacoes: str | None = None


class PrazoUpdate(BaseModel):
    id_caso: int | None = None
    id_atividade: int | None = None

    descricao: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )

    data_limite: date | None = None

    situacao: Literal[
        "Pendente",
        "Concluído",
        "Vencido"
    ] | None = None

    id_responsavel: int | None = None
    observacoes: str | None = None


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
