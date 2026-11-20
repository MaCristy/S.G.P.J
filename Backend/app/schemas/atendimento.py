
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# Define os campos compartilhados do cadastro de um atendimento.
class AtendimentoBase(BaseModel):
    id_assistido: int = Field(gt=0)
    id_caso: int | None = Field(default=None, gt=0)

    data_hora: datetime
    tipo: str = Field(min_length=1, max_length=80)
    descricao_objetiva: str = Field(min_length=1)
    encaminhamento: str | None = None


# Define os dados necessários para registrar um atendimento.
class AtendimentoCreate(AtendimentoBase):
    pass


# Define os dados retornados pela API ao consultar um atendimento.
class AtendimentoResponse(AtendimentoBase):
    model_config = ConfigDict(from_attributes=True)

    id_atendimento: int
    id_usuario_registro: int
    data_criacao: datetime
