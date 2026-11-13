
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AtendimentoBase(BaseModel):
    id_assistido: int = Field(gt=0)
    id_caso: int | None = Field(default=None, gt=0)
    id_usuario_registro: int = Field(gt=0)

    data_hora: datetime
    tipo: str = Field(min_length=1, max_length=80)
    descricao_objetiva: str = Field(min_length=1)
    encaminhamento: str | None = None


class AtendimentoCreate(AtendimentoBase):
    pass


class AtendimentoResponse(AtendimentoBase):
    model_config = ConfigDict(from_attributes=True)

    id_atendimento: int
    data_criacao: datetime
