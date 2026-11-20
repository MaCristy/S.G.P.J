
from sqlalchemy.orm import Session

from app.models.aluno import Aluno
from app.models.caso_juridico import CasoJuridico
from app.schemas.aluno import AlunoCreate


class AlunoRepository:

    # Lista todos os alunos cadastrados, ordenados pelo identificador.
    @staticmethod
    def listar(db: Session):
        return (
            db.query(Aluno)
            .order_by(Aluno.id_aluno.desc())
            .all()
        )

    # Busca um aluno pelo seu identificador.
    @staticmethod
    def buscar_por_id(db: Session, id_aluno: int):
        return (
            db.query(Aluno)
            .filter(Aluno.id_aluno == id_aluno)
            .first()
        )

    # Busca o cadastro acadêmico associado a um usuário.
    @staticmethod
    def buscar_por_usuario(db: Session, id_usuario: int):
        return (
            db.query(Aluno)
            .filter(Aluno.id_usuario == id_usuario)
            .first()
        )

    # Lista os alunos vinculados aos casos supervisionados por um professor.
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
            # Evita repetir alunos que possuem mais de um caso com o professor.
            .distinct()
            .order_by(Aluno.id_aluno.desc())
            .all()
        )

    # Busca um aluno pela matrícula acadêmica.
    @staticmethod
    def buscar_por_matricula(db: Session, matricula: str):
        return (
            db.query(Aluno)
            .filter(Aluno.matricula == matricula)
            .first()
        )

    # Cria uma nova instância de aluno com os dados recebidos.
    @staticmethod
    def criar(db: Session, dados: AlunoCreate):
        aluno = Aluno(**dados.model_dump())

        db.add(aluno)
        return aluno

    # Atualiza os campos informados no cadastro do aluno.
    @staticmethod
    def atualizar(db: Session, aluno: Aluno, dados: dict):
        for campo, valor in dados.items():
            setattr(aluno, campo, valor)

        return aluno
