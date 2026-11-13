
from sqlalchemy.orm import Session

from app.models.aluno import Aluno
from app.models.caso_juridico import CasoJuridico
from app.schemas.aluno import AlunoCreate


class AlunoRepository:

    @staticmethod
    def listar(db: Session):
        return (
            db.query(Aluno)
            .order_by(Aluno.id_aluno.desc())
            .all()
        )

    @staticmethod
    def buscar_por_id(db: Session, id_aluno: int):
        return (
            db.query(Aluno)
            .filter(Aluno.id_aluno == id_aluno)
            .first()
        )

    @staticmethod
    def buscar_por_usuario(db: Session, id_usuario: int):
        return (
            db.query(Aluno)
            .filter(Aluno.id_usuario == id_usuario)
            .first()
        )

    @staticmethod
    def listar_por_professor(db: Session, id_professor: int):
        return (
            db.query(Aluno)
            .join(
                CasoJuridico,
                CasoJuridico.id_aluno_responsavel == Aluno.id_aluno
            )
            .filter(
                CasoJuridico.id_professor_orientador == id_professor
            )
            .distinct()
            .order_by(Aluno.id_aluno.desc())
            .all()
        )

    @staticmethod
    def buscar_por_matricula(db: Session, matricula: str):
        return (
            db.query(Aluno)
            .filter(Aluno.matricula == matricula)
            .first()
        )

    @staticmethod
    def criar(db: Session, dados: AlunoCreate):
        aluno = Aluno(**dados.model_dump())

        db.add(aluno)
        return aluno

    @staticmethod
    def atualizar(db: Session, aluno: Aluno, dados: dict):
        for campo, valor in dados.items():
            setattr(aluno, campo, valor)

        return aluno
