
from pydantic import BaseModel, ConfigDict, Field


class ProfessorBase(BaseModel):

    id_usuario: int = Field(gt=0)

    identificacao_funcional: str = Field(
        min_length=1,
        max_length=50
    )

    area_vinculo: str | None = Field(
        default=None,
        max_length=100
    )

    situacao: str = Field(
        default="Ativo",
        max_length=30
    )


class ProfessorCreate(ProfessorBase):
    pass


class ProfessorUpdate(BaseModel):

    id_usuario: int | None = Field(
        default=None,
        gt=0
    )

    identificacao_funcional: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    area_vinculo: str | None = Field(
        default=None,
        max_length=100
    )

    situacao: str | None = Field(
        default=None,
        max_length=30
    )


class ProfessorResponse(ProfessorBase):

    model_config = ConfigDict(from_attributes=True)

    id_professor: int
