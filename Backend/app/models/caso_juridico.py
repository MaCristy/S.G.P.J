
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey

from app.db.base import Base


# Representa os casos jurídicos acompanhados pela Prática Jurídica.
class CasoJuridico(Base):
    __tablename__ = "casos_juridicos"

    # Identificador único do caso.
    id_caso = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # Código interno utilizado para identificar o caso no sistema.
    codigo_interno = Column(
        String(50),
        nullable=False,
        unique=True
    )

    # Vincula obrigatoriamente o caso a um assistido.
    id_assistido = Column(
        Integer,
        ForeignKey("assistidos.id_assistido"),
        nullable=False
    )

    # Armazena o título e a descrição do assunto jurídico.
    titulo_assunto = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=False)

    # Identifica a área jurídica relacionada ao caso.
    area_juridica = Column(String(100), nullable=False)

    # Define a situação inicial do caso como Em triagem.
    situacao = Column(
        String(30),
        nullable=False,
        default="Em triagem"
    )

    # Registra as datas de abertura e encerramento do caso.
    data_abertura = Column(Date, nullable=False)
    data_encerramento = Column(Date, nullable=True)

    # Vincula o caso ao aluno responsável, quando definido.
    id_aluno_responsavel = Column(
        Integer,
        ForeignKey("alunos.id_aluno"),
        nullable=True
    )

    # Vincula o caso ao professor orientador, quando definido.
    id_professor_orientador = Column(
        Integer,
        ForeignKey("professores.id_professor"),
        nullable=True
    )
