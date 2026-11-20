
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    func
)

from app.db.base import Base


# Representa os documentos armazenados no sistema.
class Documento(Base):

    __tablename__ = "documentos"

    # Identificador único do documento.
    id_documento = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # Permite vincular o documento a um caso jurídico.
    id_caso = Column(
        Integer,
        ForeignKey("casos_juridicos.id_caso"),
        nullable=True
    )

    # Permite vincular o documento a um atendimento.
    id_atendimento = Column(
        Integer,
        ForeignKey("atendimentos.id_atendimento"),
        nullable=True
    )

    # Armazena o nome original ou identificador do documento.
    nome = Column(
        String(255),
        nullable=False
    )

    # Identifica o tipo do documento.
    tipo = Column(
        String(80),
        nullable=False
    )

    # Armazena o caminho interno do arquivo no servidor.
    caminho_armazenamento = Column(
        String(500),
        nullable=False
    )

    # Registra automaticamente a data e hora de inclusão.
    data_inclusao = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    # Identifica o usuário responsável pela inclusão do documento.
    id_usuario_inclusao = Column(
        Integer,
        ForeignKey("usuarios.id_usuario"),
        nullable=False
    )

    # Define a classificação de acesso ao documento, quando informada.
    classificacao_acesso = Column(
        String(50),
        nullable=True
    )
