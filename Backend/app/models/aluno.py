from sqlalchemy import Column, Integer, String, Date, ForeignKey

from app.db.base import Base


class Aluno(Base):
    __tablename__ = "alunos"

    id_aluno = Column(
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

    matricula = Column(
        String(50),
        nullable=False,
        unique=True
    )

    curso = Column(
        String(100),
        nullable=False
    )

    periodo = Column(
        Integer,
        nullable=False
    )

    situacao_academica = Column(
        String(50),
        nullable=False
    )

    data_vinculo = Column(
        Date,
        nullable=False
    )