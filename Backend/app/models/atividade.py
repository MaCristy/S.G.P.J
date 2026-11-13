
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
    func
)

from app.db.base import Base


class Atividade(Base):

    __tablename__ = "atividades"

    id_atividade = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    id_caso = Column(
        Integer,
        ForeignKey("casos_juridicos.id_caso"),
        nullable=False
    )

    titulo = Column(String(150), nullable=False)

    descricao = Column(Text, nullable=False)

    id_responsavel = Column(
        Integer,
        ForeignKey("usuarios.id_usuario"),
        nullable=False
    )

    situacao = Column(
        String(30),
        nullable=False,
        default="Pendente"
    )

    prioridade = Column(
        String(30),
        nullable=False,
        default="Média"
    )

    data_criacao = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    data_prevista = Column(Date, nullable=True)

    data_conclusao = Column(DateTime, nullable=True)
