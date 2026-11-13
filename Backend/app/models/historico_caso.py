
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    func
)

from app.db.base import Base


class HistoricoCaso(Base):
    __tablename__ = "historico_caso"

    id_historico = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    id_caso = Column(
        Integer,
        ForeignKey("casos_juridicos.id_caso"),
        nullable=False
    )

    id_usuario_responsavel = Column(
        Integer,
        ForeignKey("usuarios.id_usuario"),
        nullable=False
    )

    tipo_ocorrencia = Column(
        String(100),
        nullable=False
    )

    descricao = Column(
        Text,
        nullable=False
    )

    data_hora = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    referencia_registro_afetado = Column(
        String(100),
        nullable=True
    )
