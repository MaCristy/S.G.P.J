
from sqlalchemy import Column, Integer, String, ForeignKey

from app.db.base import Base


# Representa os professores vinculados à Prática Jurídica.
class Professor(Base):

    __tablename__ = "professores"

    # Identificador único do professor.
    id_professor = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # Vincula o professor a uma conta de usuário do sistema.
    id_usuario = Column(
        Integer,
        ForeignKey("usuarios.id_usuario"),
        nullable=False,
        unique=True
    )

    # Armazena a identificação funcional do professor.
    identificacao_funcional = Column(
        String(50),
        nullable=False,
        unique=True
    )

    # Registra a área de atuação ou vínculo do professor.
    area_vinculo = Column(
        String(100),
        nullable=True
    )

    # Define a situação inicial do professor como Ativo.
    situacao = Column(
        String(30),
        nullable=False,
        default="Ativo"
    )
