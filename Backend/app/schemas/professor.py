
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)


# Define os campos compartilhados do cadastro de um professor.
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
        min_length=1,
        max_length=30
    )


# Define os dados necessários para cadastrar um professor.
class ProfessorCreate(ProfessorBase):
    pass


# Define os campos permitidos na atualização de um professor.
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
        min_length=1,
        max_length=30
    )

    # Impede valores nulos nos campos obrigatórios do banco.
    @model_validator(mode="before")
    @classmethod
    def validar_campos_obrigatorios(cls, dados):
        campos_obrigatorios = {
            "id_usuario",
            "identificacao_funcional",
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


# Define os dados retornados pela API ao consultar um professor.
class ProfessorResponse(ProfessorBase):
    model_config = ConfigDict(from_attributes=True)

    id_professor: int
