
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from app.repositories.professor import ProfessorRepository
from app.schemas.professor import ProfessorCreate, ProfessorUpdate


class ProfessorService:

    @staticmethod
    def listar(db: Session):
        return ProfessorRepository.listar(db)

    @staticmethod
    def buscar_por_id(db: Session, id_professor: int):
        professor = ProfessorRepository.buscar_por_id(
            db, id_professor
        )

        if not professor:
            raise LookupError("Professor não encontrado.")

        return professor

    @staticmethod
    def criar(db: Session, dados: ProfessorCreate):

        # Verifica se o usuário existe
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

        # Verifica se o usuário já possui cadastro como professor
        professor_usuario = ProfessorRepository.buscar_por_usuario(
            db, dados.id_usuario
        )

        if professor_usuario:
            raise ValueError(
                "Esse usuário já possui um cadastro como professor."
            )

        # Verifica se a identificação funcional já está cadastrada
        professor_identificacao = (
            ProfessorRepository.buscar_por_identificacao(
                db, dados.identificacao_funcional
            )
        )

        if professor_identificacao:
            raise ValueError(
                "Já existe um professor cadastrado com essa identificação funcional."
            )

        try:
            professor = ProfessorRepository.criar(db, dados)

            db.commit()
            db.refresh(professor)

            return professor

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível cadastrar o professor. "
                "Verifique os dados e os vínculos informados."
            )

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def atualizar(
        db: Session,
        id_professor: int,
        dados: ProfessorUpdate
    ):

        professor = ProfessorRepository.buscar_por_id(
            db, id_professor
        )

        if not professor:
            raise LookupError("Professor não encontrado.")

        dados_atualizacao = dados.model_dump(
            exclude_unset=True,
            exclude_none=True
        )

        # Verifica se o novo usuário existe e não pertence a outro professor
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

            outro_professor = ProfessorRepository.buscar_por_usuario(
                db, dados_atualizacao["id_usuario"]
            )

            if (
                outro_professor
                and outro_professor.id_professor != id_professor
            ):
                raise ValueError(
                    "Esse usuário já possui cadastro como professor."
                )

        # Verifica se a identificação funcional já pertence a outro professor
        if "identificacao_funcional" in dados_atualizacao:

            outra_identificacao = (
                ProfessorRepository.buscar_por_identificacao(
                    db,
                    dados_atualizacao["identificacao_funcional"]
                )
            )

            if (
                outra_identificacao
                and outra_identificacao.id_professor != id_professor
            ):
                raise ValueError(
                    "Já existe um professor cadastrado com essa identificação funcional."
                )

        try:
            professor = ProfessorRepository.atualizar(
                db, professor, dados_atualizacao
            )

            db.commit()
            db.refresh(professor)

            return professor

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível atualizar o cadastro do professor."
            )

        except Exception:
            db.rollback()
            raise

