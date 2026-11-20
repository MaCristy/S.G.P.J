
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# Define os dados necessários para registrar uma ocorrência no histórico.
class HistoricoCasoCreate(BaseModel):
    id_caso: int = Field(gt=0)

    tipo_ocorrencia: str = Field(
        min_length=1,
        max_length=100
    )

    descricao: str = Field(min_length=1)

    referencia_registro_afetado: str | None = Field(
        default=None,
        max_length=100
    )


# Define os dados retornados pela API ao consultar o histórico.
class HistoricoCasoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_historico: int
    id_caso: int
    id_usuario_responsavel: int
    tipo_ocorrencia: str
    descricao: str
    data_hora: datetime
    referencia_registro_afetado: str | None = None
