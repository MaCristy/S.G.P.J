
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DocumentoCreate(BaseModel):
    id_caso: int | None = None
    id_atendimento: int | None = None

    nome: str = Field(min_length=1, max_length=255)
    tipo: str = Field(min_length=1, max_length=80)
    caminho_armazenamento: str = Field(min_length=1, max_length=500)

    id_usuario_inclusao: int
    classificacao_acesso: str | None = Field(default=None, max_length=50)

    @model_validator(mode="after")
    def validar_referencia(self):
        if self.id_caso is None and self.id_atendimento is None:
            raise ValueError(
                "O documento deve estar vinculado a um caso jurídico "
                "ou a um atendimento."
            )

        return self


class DocumentoUpdate(BaseModel):
    id_caso: int | None = None
    id_atendimento: int | None = None

    nome: str | None = Field(default=None, min_length=1, max_length=255)
    tipo: str | None = Field(default=None, min_length=1, max_length=80)
    caminho_armazenamento: str | None = Field(
        default=None,
        min_length=1,
        max_length=500
    )
    classificacao_acesso: str | None = Field(default=None, max_length=50)


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
