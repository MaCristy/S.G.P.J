
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)


# Define os dados necessários para cadastrar um documento.
class DocumentoCreate(BaseModel):
    id_caso: int | None = Field(default=None, gt=0)
    id_atendimento: int | None = Field(default=None, gt=0)

    nome: str = Field(
        min_length=1,
        max_length=255
    )

    tipo: str = Field(
        min_length=1,
        max_length=80
    )

    caminho_armazenamento: str = Field(
        min_length=1,
        max_length=500
    )

    id_usuario_inclusao: int = Field(gt=0)

    classificacao_acesso: str | None = Field(
        default=None,
        max_length=50
    )

    # Exige que o documento esteja vinculado a um caso ou atendimento.
    @model_validator(mode="after")
    def validar_referencia(self):
        if self.id_caso is None and self.id_atendimento is None:
            raise ValueError(
                "O documento deve estar vinculado a um caso jurídico "
                "ou a um atendimento."
            )

        return self


# Define os campos permitidos na atualização de um documento.
class DocumentoUpdate(BaseModel):
    id_caso: int | None = Field(default=None, gt=0)
    id_atendimento: int | None = Field(default=None, gt=0)

    nome: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )

    tipo: str | None = Field(
        default=None,
        min_length=1,
        max_length=80
    )

    caminho_armazenamento: str | None = Field(
        default=None,
        min_length=1,
        max_length=500
    )

    classificacao_acesso: str | None = Field(
        default=None,
        max_length=50
    )

    # Impede valores nulos nos campos obrigatórios do banco.
    @model_validator(mode="before")
    @classmethod
    def validar_campos_obrigatorios(cls, dados):
        campos_obrigatorios = {
            "nome",
            "tipo",
            "caminho_armazenamento"
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


# Define os dados retornados pela API ao consultar um documento.
class DocumentoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_documento: int
    id_caso: int | None
    id_atendimento: int | None
    nome: str
    tipo: str
    caminho_armazenamento: str
    data_inclusao: datetime
    id_usuario_inclusao: int
    classificacao_acesso: str | None
