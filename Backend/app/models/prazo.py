
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


# Representa os prazos vinculados aos casos jurídicos.
class Prazo(Base):
    __tablename__ = "prazos"

    # Identificador único do prazo.
    id_prazo = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # Vincula obrigatoriamente o prazo a um caso jurídico.
    id_caso = Column(
        Integer,
        ForeignKey("casos_juridicos.id_caso"),
        nullable=False
    )

    # Permite relacionar o prazo a uma atividade específica.
    id_atividade = Column(
        Integer,
        nullable=True
    )

    # Armazena a descrição do prazo.
    descricao = Column(
        String(255),
        nullable=False
    )

    # Define a data limite para cumprimento do prazo.
    data_limite = Column(
        Date,
        nullable=False
    )

    # Controla as situações possíveis do prazo.
    situacao = Column(
        Enum(
            "Pendente de validação",
            "Pendente",
            "Concluído",
            "Vencido",
            "Rejeitado"
        ),
        nullable=False,
        default="Pendente"
    )

    # Identifica o usuário responsável pelo prazo.
    id_responsavel = Column(
        Integer,
        ForeignKey("usuarios.id_usuario"),
        nullable=False
    )

    # Armazena observações adicionais sobre o prazo.
    observacoes = Column(
        Text,
        nullable=True
    )

    # Registra a data e hora de conclusão, quando aplicável.
    data_conclusao = Column(
        DateTime,
        nullable=True
    )

    # Armazena a justificativa quando o prazo é rejeitado.
    motivo_rejeicao = Column(
        Text,
        nullable=True
    )
