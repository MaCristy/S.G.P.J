
from datetime import date

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)


# Define os dados obrigatórios para cadastro de um aluno.
class AlunoBase(BaseModel):
    id_usuario: int = Field(gt=0)
    matricula: str = Field(min_length=1, max_length=50)
    curso: str = Field(min_length=1, max_length=100)
    periodo: int = Field(gt=0)
    situacao_academica: str = Field(min_length=1, max_length=50)
    data_vinculo: date


# Define os dados aceitos na criação de um aluno.
class AlunoCreate(AlunoBase):
    pass


# Define os campos que podem ser alterados no cadastro do aluno.
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

    # Impede que campos obrigatórios do banco recebam null em atualizações.
    @model_validator(mode="before")
    @classmethod
    def validar_campos_nao_nulos(cls, dados):
        campos_obrigatorios = {
            "id_usuario",
            "matricula",
            "curso",
            "periodo",
            "situacao_academica",
            "data_vinculo"
        }

        if isinstance(dados, dict):
            campos_nulos = [
                campo
                for campo in campos_obrigatorios
                if campo in dados and dados[campo] is None
            ]

            if campos_nulos:
                raise ValueError(
                    f"Os seguintes campos não podem receber null: "
                    f"{', '.join(sorted(campos_nulos))}."
                )

        return dados


# Define os dados retornados pela API ao consultar um aluno.
class AlunoResponse(AlunoBase):
    model_config = ConfigDict(from_attributes=True)

    id_aluno: int
