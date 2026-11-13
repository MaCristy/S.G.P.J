
from sqlalchemy.orm import Session

from app.models.professor import Professor
from app.schemas.professor import ProfessorCreate


class ProfessorRepository:

    @staticmethod
    def listar(db: Session):
        return (
            db.query(Professor)
            .order_by(Professor.id_professor.desc())
            .all()
        )

    @staticmethod
    def buscar_por_id(db: Session, id_professor: int):
        return (
            db.query(Professor)
            .filter(Professor.id_professor == id_professor)
            .first()
        )

    @staticmethod
    def buscar_por_usuario(db: Session, id_usuario: int):
        return (
            db.query(Professor)
            .filter(Professor.id_usuario == id_usuario)
            .first()
        )

    @staticmethod
    def buscar_por_identificacao(db: Session, identificacao: str):
        return (
            db.query(Professor)
            .filter(
                Professor.identificacao_funcional == identificacao
            )
            .first()
        )

    @staticmethod
    def criar(db: Session, dados: ProfessorCreate):
        professor = Professor(
            id_usuario=dados.id_usuario,
            identificacao_funcional=dados.identificacao_funcional,
            area_vinculo=dados.area_vinculo,
            situacao=dados.situacao
        )

        db.add(professor)

        return professor

    @staticmethod
    def atualizar(db: Session, professor: Professor, dados: dict):
        for campo, valor in dados.items():
            setattr(professor, campo, valor)

        return professor
