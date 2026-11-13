
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    func
)

from app.db.base import Base


class Documento(Base):

    __tablename__ = "documentos"

    id_documento = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    id_caso = Column(
        Integer,
        ForeignKey("casos_juridicos.id_caso"),
        nullable=True
    )

    id_atendimento = Column(
        Integer,
        ForeignKey("atendimentos.id_atendimento"),
        nullable=True
    )

    nome = Column(
        String(255),
        nullable=False
    )

    tipo = Column(
        String(80),
        nullable=False
    )

    caminho_armazenamento = Column(
        String(500),
        nullable=False
    )

    data_inclusao = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    id_usuario_inclusao = Column(
        Integer,
        ForeignKey("usuarios.id_usuario"),
        nullable=False
    )

    classificacao_acesso = Column(
        String(50),
        nullable=True
    )
