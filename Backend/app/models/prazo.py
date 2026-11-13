
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Text,
    ForeignKey,
    Enum
)

from app.db.base import Base


class Prazo(Base):
    __tablename__ = "prazos"

    id_prazo = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    id_caso = Column(
        Integer,
        ForeignKey("casos_juridicos.id_caso"),
        nullable=False
    )

    id_atividade = Column(
        Integer,
        nullable=True
    )

    descricao = Column(
        String(255),
        nullable=False
    )

    data_limite = Column(
        Date,
        nullable=False
    )

    situacao = Column(
        Enum("Pendente", "Concluído", "Vencido"),
        nullable=False,
        default="Pendente"
    )

    id_responsavel = Column(
        Integer,
        ForeignKey("usuarios.id_usuario"),
        nullable=False
    )

    observacoes = Column(
        Text,
        nullable=True
    )

    data_conclusao = Column(
        DateTime,
        nullable=True
    )
