
from sqlalchemy.orm import Session

from app.models.documento import Documento


class DocumentoRepository:

    @staticmethod
    def listar(db: Session):
        return (
            db.query(Documento)
            .order_by(Documento.data_inclusao.desc())
            .all()
        )

    @staticmethod
    def buscar_por_id(db: Session, id_documento: int):
        return (
            db.query(Documento)
            .filter(Documento.id_documento == id_documento)
            .first()
        )

    @staticmethod
    def listar_por_caso(db: Session, id_caso: int):
        return (
            db.query(Documento)
            .filter(Documento.id_caso == id_caso)
            .order_by(Documento.data_inclusao.desc())
            .all()
        )

    @staticmethod
    def listar_por_atendimento(db: Session, id_atendimento: int):
        return (
            db.query(Documento)
            .filter(Documento.id_atendimento == id_atendimento)
            .order_by(Documento.data_inclusao.desc())
            .all()
        )

    @staticmethod
    def criar(db: Session, dados: dict):
        documento = Documento(**dados)

        db.add(documento)
        db.commit()
        db.refresh(documento)

        return documento

    @staticmethod
    def atualizar(db: Session, documento: Documento, dados: dict):
        for campo, valor in dados.items():
            setattr(documento, campo, valor)

        db.commit()
        db.refresh(documento)

        return documento
