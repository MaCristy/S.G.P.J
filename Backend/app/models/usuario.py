
from sqlalchemy import Column, Integer, String, DateTime, func

from app.db.base import Base


# Representa os usuários cadastrados no sistema.
class Usuario(Base):
    __tablename__ = "usuarios"

    # Identificador único do usuário.
    id_usuario = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # Armazena o nome completo do usuário.
    nome = Column(
        String(150),
        nullable=False
    )

    # Armazena o e-mail institucional, que deve ser único.
    email_institucional = Column(
        String(150),
        nullable=False,
        unique=True
    )

    # Armazena a senha protegida utilizada na autenticação.
    senha_armazenada = Column(
        String(255),
        nullable=False
    )

    # Identifica o perfil de acesso do usuário.
    perfil = Column(
        String(50),
        nullable=False
    )

    # Define a situação inicial da conta como Ativo.
    situacao_conta = Column(
        String(30),
        nullable=False,
        server_default="Ativo"
    )

    # Registra automaticamente a data e hora de criação da conta.
    data_criacao = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    # Armazena a data e hora do último acesso, quando disponível.
    ultimo_acesso = Column(
        DateTime,
        nullable=True
    )
