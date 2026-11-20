
from sqlalchemy import Column, Integer, String, Date, ForeignKey

from app.db.base import Base


# Representa o cadastro acadêmico dos alunos do sistema.
class Aluno(Base):
    __tablename__ = "alunos"

    # Identificador único do cadastro do aluno.
    id_aluno = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # Vincula o cadastro acadêmico a um usuário.
    # Cada usuário pode possuir apenas um cadastro de aluno.
    id_usuario = Column(
        Integer,
        ForeignKey("usuarios.id_usuario"),
        nullable=False,
        unique=True
    )

    # Armazena a matrícula acadêmica, que deve ser única.
    matricula = Column(
        String(50),
        nullable=False,
        unique=True
    )

    # Registra o curso em que o aluno está matriculado.
    curso = Column(
        String(100),
        nullable=False
    )

    # Armazena o período acadêmico atual do aluno.
    periodo = Column(
        Integer,
        nullable=False
    )

    # Registra a situação acadêmica do aluno.
    situacao_academica = Column(
        String(50),
        nullable=False
    )

    # Registra a data de início do vínculo acadêmico.
    data_vinculo = Column(
        Date,
        nullable=False
    )
