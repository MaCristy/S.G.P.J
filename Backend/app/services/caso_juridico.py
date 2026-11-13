from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.caso_juridico import CasoJuridicoRepository
from app.repositories.assistido import AssistidoRepository
from app.schemas.caso_juridico import CasoJuridicoCreate


class CasoJuridicoService:

    @staticmethod
    def listar(db: Session):
        return CasoJuridicoRepository.listar(db)

    @staticmethod
    def buscar_por_id(db: Session, id_caso: int):
        caso = CasoJuridicoRepository.buscar_por_id(db, id_caso)

        if not caso:
            raise LookupError("Caso jurídico não encontrado.")

        return caso

    @staticmethod
    def listar_por_assistido(db: Session, id_assistido: int):
        assistido = AssistidoRepository.buscar_por_id(db, id_assistido)

        if not assistido:
            raise LookupError("Assistido não encontrado.")

        return CasoJuridicoRepository.listar_por_assistido(
            db, id_assistido
        )

    @staticmethod
    def criar(db: Session, dados: CasoJuridicoCreate):
        # Verifica se o assistido existe
        assistido = AssistidoRepository.buscar_por_id(
            db, dados.id_assistido
        )

        if not assistido:
            raise LookupError("Assistido não encontrado.")

        # Verifica se o código interno já está cadastrado
        codigo_existente = CasoJuridicoRepository.buscar_por_codigo(
            db, dados.codigo_interno
        )

        if codigo_existente:
            raise ValueError("Já existe um caso com esse código interno.")

        # Verifica se o aluno responsável existe, quando informado
        if dados.id_aluno_responsavel is not None:
            aluno = db.execute(
                text("""
                    SELECT id_aluno
                    FROM alunos
                    WHERE id_aluno = :id_aluno
                """),
                {"id_aluno": dados.id_aluno_responsavel}
            ).first()

            if not aluno:
                raise LookupError("Aluno responsável não encontrado.")

        # Verifica se o professor orientador existe, quando informado
        if dados.id_professor_orientador is not None:
            professor = db.execute(
                text("""
                    SELECT id_professor
                    FROM professores
                    WHERE id_professor = :id_professor
                """),
                {"id_professor": dados.id_professor_orientador}
            ).first()

            if not professor:
                raise LookupError("Professor orientador não encontrado.")

        try:
            caso = CasoJuridicoRepository.criar(db, dados)

            db.commit()
            db.refresh(caso)

            return caso

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível cadastrar o caso jurídico. "
                "Verifique os dados e os relacionamentos informados."
            )

        except Exception:
            db.rollback()
            raise