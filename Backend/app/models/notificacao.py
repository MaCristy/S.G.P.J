
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    func
)

from app.db.base import Base


# Representa as notificações individuais dos usuários.
class Notificacao(Base):
    __tablename__ = "notificacoes"

    # Identificador único da notificação.
    id_notificacao = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # Usuário que receberá a notificação.
    id_usuario_destinatario = Column(
        Integer,
        ForeignKey("usuarios.id_usuario"),
        nullable=False
    )

    # Usuário responsável pelo acontecimento, quando aplicável.
    id_usuario_origem = Column(
        Integer,
        ForeignKey("usuarios.id_usuario"),
        nullable=True
    )

    # Caso jurídico relacionado, quando aplicável.
    id_caso = Column(
        Integer,
        ForeignKey("casos_juridicos.id_caso"),
        nullable=True
    )

    # Classificação da notificação.
    tipo = Column(
        String(50),
        nullable=False
    )

    # Título apresentado ao usuário.
    titulo = Column(
        String(150),
        nullable=False
    )

    # Conteúdo da notificação.
    mensagem = Column(
        Text,
        nullable=False
    )

    # Endereço interno para navegação, quando aplicável.
    link = Column(
        String(255),
        nullable=True
    )

    # Indica se a notificação já foi visualizada.
    lida = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0"
    )

    # Data e hora em que a notificação foi lida.
    data_leitura = Column(
        DateTime,
        nullable=True
    )

    # Data e hora de criação da notificação.
    data_criacao = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )
