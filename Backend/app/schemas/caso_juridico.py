
from datetime import date
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)


# Define as situações permitidas para um caso jurídico.
SituacaoCaso = Literal[
    "Em triagem",
    "Aberto",
    "Em Andamento",
    "Suspenso",
    "Encerrado"
]


# Define os campos compartilhados do cadastro de um caso jurídico.
class CasoJuridicoBase(BaseModel):
    codigo_interno: str = Field(
        min_length=1,
        max_length=50
    )

    id_assistido: int = Field(gt=0)

    titulo_assunto: str = Field(
        min_length=1,
        max_length=200
    )

    descricao: str = Field(min_length=1)

    area_juridica: str = Field(
        min_length=1,
        max_length=100
    )

    situacao: SituacaoCaso = "Em triagem"

    data_abertura: date
    data_encerramento: date | None = None

    id_aluno_responsavel: int | None = Field(
        default=None,
        gt=0
    )

    id_professor_orientador: int | None = Field(
        default=None,
        gt=0
    )


# Define os dados necessários para cadastrar um caso jurídico.
class CasoJuridicoCreate(CasoJuridicoBase):
    pass


# Define os campos permitidos na atualização de um caso jurídico.
class CasoJuridicoUpdate(BaseModel):
    codigo_interno: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    id_assistido: int | None = Field(
        default=None,
        gt=0
    )

    titulo_assunto: str | None = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    descricao: str | None = Field(
        default=None,
        min_length=1
    )

    area_juridica: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    situacao: SituacaoCaso | None = None
    data_abertura: date | None = None
    data_encerramento: date | None = None

    id_aluno_responsavel: int | None = Field(
        default=None,
        gt=0
    )

    id_professor_orientador: int | None = Field(
        default=None,
        gt=0
    )

    # Impede valores nulos nos campos obrigatórios do banco.
    @model_validator(mode="before")
    @classmethod
    def validar_campos_obrigatorios(cls, dados):
        campos_obrigatorios = {
            "codigo_interno",
            "id_assistido",
            "titulo_assunto",
            "descricao",
            "area_juridica",
            "situacao",
            "data_abertura"
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


# Define os dados retornados pela API ao consultar um caso jurídico.
class CasoJuridicoResponse(CasoJuridicoBase):
    model_config = ConfigDict(from_attributes=True)

    id_caso: int
