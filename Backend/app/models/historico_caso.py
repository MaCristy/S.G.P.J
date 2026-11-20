
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    func
)

from app.db.base import Base


# Representa os registros de histórico dos casos jurídicos.
class HistoricoCaso(Base):
    __tablename__ = "historico_caso"

    # Identificador único do registro histórico.
    id_historico = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # Vincula o histórico ao caso jurídico correspondente.
    id_caso = Column(
        Integer,
        ForeignKey("casos_juridicos.id_caso"),
        nullable=False
    )

    # Identifica o usuário responsável pela ocorrência registrada.
    id_usuario_responsavel = Column(
        Integer,
        ForeignKey("usuarios.id_usuario"),
        nullable=False
    )

    # Classifica o tipo de ocorrência registrada no histórico.
    tipo_ocorrencia = Column(
        String(100),
        nullable=False
    )

    # Armazena a descrição detalhada da ocorrência.
    descricao = Column(
        Text,
        nullable=False
    )

    # Registra automaticamente a data e hora da ocorrência.
    data_hora = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    # Identifica o registro afetado pela ocorrência, quando aplicável.
    referencia_registro_afetado = Column(
        String(100),
        nullable=True
    )
