
from sqlalchemy.orm import Session

from app.models.prazo import Prazo


class PrazoRepository:

    @staticmethod
    def listar(db: Session):
        return (
            db.query(Prazo)
            .order_by(Prazo.data_limite.asc())
            .all()
        )

    @staticmethod
    def buscar_por_id(db: Session, id_prazo: int):
        return (
            db.query(Prazo)
            .filter(Prazo.id_prazo == id_prazo)
            .first()
        )

    @staticmethod
    def listar_por_caso(db: Session, id_caso: int):
        return (
            db.query(Prazo)
            .filter(Prazo.id_caso == id_caso)
            .order_by(Prazo.data_limite.asc())
            .all()
        )

    @staticmethod
    def listar_por_responsavel(db: Session, id_responsavel: int):
        return (
            db.query(Prazo)
            .filter(Prazo.id_responsavel == id_responsavel)
            .order_by(Prazo.data_limite.asc())
            .all()
        )

    @staticmethod
    def criar(db: Session, dados: dict):
        prazo = Prazo(**dados)

        db.add(prazo)
        db.commit()
        db.refresh(prazo)

        return prazo

    @staticmethod
    def atualizar(db: Session, prazo: Prazo, dados: dict):
        for campo, valor in dados.items():
            setattr(prazo, campo, valor)

        db.commit()
        db.refresh(prazo)

        return prazo
