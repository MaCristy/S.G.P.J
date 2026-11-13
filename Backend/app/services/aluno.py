
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from app.repositories.aluno import AlunoRepository
from app.repositories.professor import ProfessorRepository
from app.schemas.aluno import AlunoCreate, AlunoUpdate


class AlunoService:

    @staticmethod
    def listar(db: Session):
        return AlunoRepository.listar(db)

    @staticmethod
    def listar_por_professor(db: Session, id_usuario: int):
        professor = ProfessorRepository.buscar_por_usuario(
            db, id_usuario
        )

        if not professor:
            raise LookupError(
                "Cadastro de professor não encontrado."
            )

        if professor.situacao != "Ativo":
            raise PermissionError(
                "O cadastro do professor não está ativo."
            )

        return AlunoRepository.listar_por_professor(
            db, professor.id_professor
        )

    @staticmethod
    def buscar_por_usuario(db: Session, id_usuario: int):
        aluno = AlunoRepository.buscar_por_usuario(
            db, id_usuario
        )

        if not aluno:
            raise LookupError("Cadastro de aluno não encontrado.")

        return aluno

    @staticmethod
    def buscar_por_id(db: Session, id_aluno: int):
        aluno = AlunoRepository.buscar_por_id(db, id_aluno)

        if not aluno:
            raise LookupError("Aluno não encontrado.")

        return aluno

    @staticmethod
    def criar(db: Session, dados: AlunoCreate):

        usuario = db.execute(
            text("""
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = :id_usuario
            """),
            {"id_usuario": dados.id_usuario}
        ).first()

        if not usuario:
            raise LookupError("Usuário informado não encontrado.")

        aluno_usuario = AlunoRepository.buscar_por_usuario(
            db, dados.id_usuario
        )

        if aluno_usuario:
            raise ValueError(
                "Esse usuário já possui um cadastro como aluno."
            )

        aluno_matricula = AlunoRepository.buscar_por_matricula(
            db, dados.matricula
        )

        if aluno_matricula:
            raise ValueError(
                "Já existe um aluno cadastrado com essa matrícula."
            )

        try:
            aluno = AlunoRepository.criar(db, dados)

            db.commit()
            db.refresh(aluno)

            return aluno

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível cadastrar o aluno. "
                "Verifique os dados e os vínculos informados."
            )

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def atualizar(db: Session, id_aluno: int, dados: AlunoUpdate):

        aluno = AlunoRepository.buscar_por_id(db, id_aluno)

        if not aluno:
            raise LookupError("Aluno não encontrado.")

        dados_atualizacao = dados.model_dump(
            exclude_unset=True,
            exclude_none=True
        )

        if "id_usuario" in dados_atualizacao:

            usuario = db.execute(
                text("""
                    SELECT id_usuario
                    FROM usuarios
                    WHERE id_usuario = :id_usuario
                """),
                {"id_usuario": dados_atualizacao["id_usuario"]}
            ).first()

            if not usuario:
                raise LookupError("Usuário informado não encontrado.")

            outro_aluno = AlunoRepository.buscar_por_usuario(
                db, dados_atualizacao["id_usuario"]
            )

            if outro_aluno and outro_aluno.id_aluno != id_aluno:
                raise ValueError(
                    "Esse usuário já possui cadastro como aluno."
                )

        if "matricula" in dados_atualizacao:

            outra_matricula = AlunoRepository.buscar_por_matricula(
                db, dados_atualizacao["matricula"]
            )

            if outra_matricula and outra_matricula.id_aluno != id_aluno:
                raise ValueError(
                    "Já existe um aluno cadastrado com essa matrícula."
                )

        try:
            aluno = AlunoRepository.atualizar(
                db, aluno, dados_atualizacao
            )

            db.commit()
            db.refresh(aluno)

            return aluno

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível atualizar o cadastro do aluno."
            )

        except Exception:
            db.rollback()
            raise
