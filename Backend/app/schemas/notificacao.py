
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# Define os dados retornados pela API ao consultar uma notificação.
class NotificacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_notificacao: int
    id_usuario_destinatario: int
    id_usuario_origem: int | None
    id_caso: int | None
    tipo: str
    titulo: str
    mensagem: str
    link: str | None
    lida: bool
    data_leitura: datetime | None
    data_criacao: datetime
