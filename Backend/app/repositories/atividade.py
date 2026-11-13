
from sqlalchemy.orm import Session

from app.models.atividade import Atividade
from app.schemas.atividade import AtividadeCreate


class AtividadeRepository:

    @staticmethod
    def listar(db: Session):
        return (
            db.query(Atividade)
            .order_by(Atividade.id_atividade.desc())
            .all()
        )

    @staticmethod
    def buscar_por_id(db: Session, id_atividade: int):
        return (
            db.query(Atividade)
            .filter(Atividade.id_atividade == id_atividade)
            .first()
        )

    @staticmethod
    def listar_por_caso(db: Session, id_caso: int):
        return (
            db.query(Atividade)
            .filter(Atividade.id_caso == id_caso)
            .order_by(Atividade.id_atividade.desc())
            .all()
        )

    @staticmethod
    def listar_por_responsavel(db: Session, id_responsavel: int):
        return (
            db.query(Atividade)
            .filter(Atividade.id_responsavel == id_responsavel)
            .order_by(Atividade.id_atividade.desc())
            .all()
        )

    @staticmethod
    def criar(db: Session, dados: AtividadeCreate):
        atividade = Atividade(
            id_caso=dados.id_caso,
            titulo=dados.titulo,
            descricao=dados.descricao,
            id_responsavel=dados.id_responsavel,
            situacao=dados.situacao,
            prioridade=dados.prioridade,
            data_prevista=dados.data_prevista
        )

        db.add(atividade)

        return atividade

    @staticmethod
    def atualizar(
        db: Session,
        atividade: Atividade,
        dados: dict
    ):
        for campo, valor in dados.items():
            setattr(atividade, campo, valor)

        return atividade
