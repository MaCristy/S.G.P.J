
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


# Representa as atividades vinculadas aos casos jurídicos.
class Atividade(Base):

    __tablename__ = "atividades"

    # Identificador único da atividade.
    id_atividade = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # Vincula obrigatoriamente a atividade a um caso jurídico.
    id_caso = Column(
        Integer,
        ForeignKey("casos_juridicos.id_caso"),
        nullable=False
    )

    # Armazena o título que identifica a atividade.
    titulo = Column(String(150), nullable=False)

    # Guarda a descrição e as informações da atividade.
    descricao = Column(Text, nullable=False)

    # Identifica o usuário responsável pela execução da atividade.
    id_responsavel = Column(
        Integer,
        ForeignKey("usuarios.id_usuario"),
        nullable=False
    )

    # Define a situação inicial da atividade como Pendente.
    situacao = Column(
        String(30),
        nullable=False,
        default="Pendente"
    )

    # Define a prioridade inicial da atividade como Média.
    prioridade = Column(
        String(30),
        nullable=False,
        default="Média"
    )

    # Registra automaticamente a data e hora de criação.
    data_criacao = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    # Armazena a data prevista para realização da atividade.
    data_prevista = Column(Date, nullable=True)

    # Registra a data e hora de conclusão, quando aplicável.
    data_conclusao = Column(DateTime, nullable=True)
