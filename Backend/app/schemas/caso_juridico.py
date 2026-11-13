from datetime import date
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


SituacaoCaso = Literal[
    "Em triagem",
    "Aberto",
    "Em Andamento",
    "Suspenso",
    "Encerrado"
]


class CasoJuridicoBase(BaseModel):
    codigo_interno: str = Field(min_length=1, max_length=50)
    id_assistido: int = Field(gt=0)
    titulo_assunto: str = Field(min_length=1, max_length=200)
    descricao: str = Field(min_length=1)
    area_juridica: str = Field(min_length=1, max_length=100)
    situacao: SituacaoCaso = "Em triagem"
    data_abertura: date
    data_encerramento: date | None = None
    id_aluno_responsavel: int | None = Field(default=None, gt=0)
    id_professor_orientador: int | None = Field(default=None, gt=0)


class CasoJuridicoCreate(CasoJuridicoBase):
    pass


class CasoJuridicoUpdate(BaseModel):
    codigo_interno: str | None = Field(default=None, min_length=1, max_length=50)
    id_assistido: int | None = Field(default=None, gt=0)
    titulo_assunto: str | None = Field(default=None, min_length=1, max_length=200)
    descricao: str | None = Field(default=None, min_length=1)
    area_juridica: str | None = Field(default=None, min_length=1, max_length=100)
    situacao: SituacaoCaso | None = None
    data_abertura: date | None = None
    data_encerramento: date | None = None
    id_aluno_responsavel: int | None = Field(default=None, gt=0)
    id_professor_orientador: int | None = Field(default=None, gt=0)


class CasoJuridicoResponse(CasoJuridicoBase):
    model_config = ConfigDict(from_attributes=True)

    id_caso: int