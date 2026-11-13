
from sqlalchemy.orm import Session

from app.models.historico_caso import HistoricoCaso


class HistoricoCasoRepository:

    @staticmethod
    def listar(db: Session):
        return (
            db.query(HistoricoCaso)
            .order_by(HistoricoCaso.data_hora.desc())
            .all()
        )

    @staticmethod
    def buscar_por_id(db: Session, id_historico: int):
        return (
            db.query(HistoricoCaso)
            .filter(
                HistoricoCaso.id_historico == id_historico
            )
            .first()
        )

    @staticmethod
    def listar_por_caso(db: Session, id_caso: int):
        return (
            db.query(HistoricoCaso)
            .filter(HistoricoCaso.id_caso == id_caso)
            .order_by(HistoricoCaso.data_hora.desc())
            .all()
        )

    @staticmethod
    def listar_por_usuario(
        db: Session,
        id_usuario_responsavel: int
    ):
        return (
            db.query(HistoricoCaso)
            .filter(
                HistoricoCaso.id_usuario_responsavel
                == id_usuario_responsavel
            )
            .order_by(HistoricoCaso.data_hora.desc())
            .all()
        )

    @staticmethod
    def criar(db: Session, dados: dict):
        historico = HistoricoCaso(**dados)

        db.add(historico)
        db.commit()
        db.refresh(historico)

        return historico
