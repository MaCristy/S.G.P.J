
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey

from app.db.base import Base


class CasoJuridico(Base):
    __tablename__ = "casos_juridicos"

    id_caso = Column(Integer, primary_key=True, autoincrement=True)

    codigo_interno = Column(String(50), nullable=False, unique=True)

    id_assistido = Column(
        Integer,
        ForeignKey("assistidos.id_assistido"),
        nullable=False
    )

    titulo_assunto = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=False)
    area_juridica = Column(String(100), nullable=False)

    situacao = Column(
        String(30),
        nullable=False,
        default="Em triagem"
    )

    data_abertura = Column(Date, nullable=False)
    data_encerramento = Column(Date, nullable=True)

    id_aluno_responsavel = Column(Integer, nullable=True)
    id_professor_orientador = Column(Integer, nullable=True)
