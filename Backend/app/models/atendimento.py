
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func

from app.db.base import Base


# Representa os atendimentos realizados pela Prática Jurídica.
class Atendimento(Base):
    __tablename__ = "atendimentos"

    # Identificador único do atendimento.
    id_atendimento = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # Vincula obrigatoriamente o atendimento a um assistido.
    id_assistido = Column(
        Integer,
        ForeignKey("assistidos.id_assistido"),
        nullable=False
    )

    # Permite associar o atendimento a um caso jurídico, quando aplicável.
    id_caso = Column(
        Integer,
        ForeignKey("casos_juridicos.id_caso"),
        nullable=True
    )

    # Identifica o usuário responsável pelo registro do atendimento.
    id_usuario_registro = Column(
        Integer,
        ForeignKey("usuarios.id_usuario"),
        nullable=False
    )

    # Armazena a data e a hora em que o atendimento ocorreu.
    data_hora = Column(
        DateTime,
        nullable=False
    )

    # Identifica a modalidade ou o tipo de atendimento realizado.
    tipo = Column(
        String(80),
        nullable=False
    )

    # Registra a descrição objetiva do atendimento.
    descricao_objetiva = Column(
        Text,
        nullable=False
    )

    # Armazena os encaminhamentos definidos durante o atendimento.
    encaminhamento = Column(
        Text,
        nullable=True
    )

    # Registra automaticamente a data e hora de criação do cadastro.
    data_criacao = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )
