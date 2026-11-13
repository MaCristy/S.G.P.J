
from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base


class Professor(Base):

    __tablename__ = "professores"

    id_professor = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    id_usuario = Column(
        Integer,
        ForeignKey("usuarios.id_usuario"),
        nullable=False,
        unique=True
    )

    identificacao_funcional = Column(
        String(50),
        nullable=False,
        unique=True
    )

    area_vinculo = Column(
        String(100),
        nullable=True
    )

    situacao = Column(
        String(30),
        nullable=False,
        default="Ativo"
    )
