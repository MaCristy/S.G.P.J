
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func

from app.db.base import Base


# Representa os assistidos cadastrados no sistema.
class Assistido(Base):
    __tablename__ = "assistidos"

    # Identificador único do assistido.
    id_assistido = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # Identifica o aluno responsável pelo cadastro, quando aplicável.
    id_aluno_cadastro = Column(
        Integer,
        ForeignKey("alunos.id_aluno"),
        nullable=True
    )

    # Armazena o nome completo do assistido.
    nome_completo = Column(
        String(200),
        nullable=False
    )

    # Identificador cadastral único utilizado no sistema.
    identificador_cadastral = Column(
        String(50),
        nullable=False,
        unique=True
    )

    # Armazena as informações de contato do assistido.
    contato = Column(
        String(100),
        nullable=False
    )

    # Permite registrar o endereço, quando informado.
    endereco = Column(
        Text,
        nullable=True
    )

    # Guarda observações administrativas complementares.
    observacoes_administrativas = Column(
        Text,
        nullable=True
    )

    # Registra automaticamente a data e hora do cadastro.
    data_cadastro = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    # Define a situação inicial do assistido como Ativo.
    situacao = Column(
        String(30),
        nullable=False,
        server_default="Ativo"
    )
