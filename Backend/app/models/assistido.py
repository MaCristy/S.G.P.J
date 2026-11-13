
from sqlalchemy import Column, Integer, String, Text, DateTime, func

from app.db.base import Base


class Assistido(Base):
    __tablename__ = "assistidos"

    id_assistido = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    nome_completo = Column(
        String(200),
        nullable=False
    )

    identificador_cadastral = Column(
        String(50),
        nullable=False,
        unique=True
    )

    contato = Column(
        String(100),
        nullable=False
    )

    endereco = Column(
        Text,
        nullable=True
    )

    observacoes_administrativas = Column(
        Text,
        nullable=True
    )

    data_cadastro = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    situacao = Column(
        String(30),
        nullable=False,
        server_default="Ativo"
    )
