from datetime import date
from pydantic import BaseModel, ConfigDict, Field


class AlunoBase(BaseModel):
    id_usuario: int = Field(gt=0)
    matricula: str = Field(min_length=1, max_length=50)
    curso: str = Field(min_length=1, max_length=100)
    periodo: int = Field(gt=0)
    situacao_academica: str = Field(min_length=1, max_length=50)
    data_vinculo: date


class AlunoCreate(AlunoBase):
    pass


class AlunoUpdate(BaseModel):
    id_usuario: int | None = Field(default=None, gt=0)
    matricula: str | None = Field(default=None, min_length=1, max_length=50)
    curso: str | None = Field(default=None, min_length=1, max_length=100)
    periodo: int | None = Field(default=None, gt=0)
    situacao_academica: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )
    data_vinculo: date | None = None


class AlunoResponse(AlunoBase):
    model_config = ConfigDict(from_attributes=True)

    id_aluno: int