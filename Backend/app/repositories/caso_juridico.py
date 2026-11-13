from sqlalchemy.orm import Session

from app.models.caso_juridico import CasoJuridico
from app.schemas.caso_juridico import CasoJuridicoCreate


class CasoJuridicoRepository:

    @staticmethod
    def listar(db: Session):
        return (
            db.query(CasoJuridico)
            .order_by(CasoJuridico.id_caso.desc())
            .all()
        )

    @staticmethod
    def buscar_por_id(db: Session, id_caso: int):
        return (
            db.query(CasoJuridico)
            .filter(CasoJuridico.id_caso == id_caso)
            .first()
        )

    @staticmethod
    def buscar_por_codigo(db: Session, codigo_interno: str):
        return (
            db.query(CasoJuridico)
            .filter(CasoJuridico.codigo_interno == codigo_interno)
            .first()
        )

    @staticmethod
    def listar_por_assistido(db: Session, id_assistido: int):
        return (
            db.query(CasoJuridico)
            .filter(CasoJuridico.id_assistido == id_assistido)
            .order_by(CasoJuridico.id_caso.desc())
            .all()
        )

    @staticmethod
    def criar(db: Session, dados: CasoJuridicoCreate):
        caso = CasoJuridico(**dados.model_dump())

        db.add(caso)
        return caso

    @staticmethod
    def atualizar(db: Session, caso: CasoJuridico, dados: dict):
        for campo, valor in dados.items():
            setattr(caso, campo, valor)

        return caso
        