
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from app.db.base import Base


class Atendimento(Base):
    __tablename__ = "atendimentos"

    id_atendimento = Column(Integer, primary_key=True, autoincrement=True)

    id_assistido = Column(
        Integer,
        ForeignKey("assistidos.id_assistido"),
        nullable=False
    )

    id_caso = Column(
        Integer,
        ForeignKey("casos_juridicos.id_caso"),
        nullable=True
    )

    id_usuario_registro = Column(
        Integer,
        ForeignKey("usuarios.id_usuario"),
        nullable=False
    )

    data_hora = Column(DateTime, nullable=False)
    tipo = Column(String(80), nullable=False)
    descricao_objetiva = Column(Text, nullable=False)
    encaminhamento = Column(Text, nullable=True)

    data_criacao = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )
