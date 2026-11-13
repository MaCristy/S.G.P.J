
from sqlalchemy.orm import Session

from app.models.atendimento import Atendimento
from app.schemas.atendimento import AtendimentoCreate


class AtendimentoRepository:

    @staticmethod
    def listar(db: Session):
        return (
            db.query(Atendimento)
            .order_by(Atendimento.data_hora.desc())
            .all()
        )

    @staticmethod
    def buscar_por_id(db: Session, id_atendimento: int):
        return (
            db.query(Atendimento)
            .filter(Atendimento.id_atendimento == id_atendimento)
            .first()
        )

    @staticmethod
    def listar_por_assistido(db: Session, id_assistido: int):
        return (
            db.query(Atendimento)
            .filter(Atendimento.id_assistido == id_assistido)
            .order_by(Atendimento.data_hora.desc())
            .all()
        )

    @staticmethod
    def criar(db: Session, dados: AtendimentoCreate):
        atendimento = Atendimento(**dados.model_dump())

        db.add(atendimento)
        db.flush()
        db.refresh(atendimento)

        return atendimento
