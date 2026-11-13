
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.atendimento import AtendimentoRepository
from app.repositories.assistido import AssistidoRepository
from app.schemas.atendimento import AtendimentoCreate


class AtendimentoService:

    @staticmethod
    def listar(db: Session):
        return AtendimentoRepository.listar(db)

    @staticmethod
    def buscar_por_id(db: Session, id_atendimento: int):
        atendimento = AtendimentoRepository.buscar_por_id(
            db, id_atendimento
        )

        if not atendimento:
            raise LookupError("Atendimento não encontrado.")

        return atendimento

    @staticmethod
    def listar_por_assistido(db: Session, id_assistido: int):
        assistido = AssistidoRepository.buscar_por_id(
            db, id_assistido
        )

        if not assistido:
            raise LookupError("Assistido não encontrado.")

        return AtendimentoRepository.listar_por_assistido(
            db, id_assistido
        )

    @staticmethod
    def criar(db: Session, dados: AtendimentoCreate):

        # Verifica se o assistido existe.
        assistido = AssistidoRepository.buscar_por_id(
            db, dados.id_assistido
        )

        if not assistido:
            raise LookupError("Assistido não encontrado.")

        # Verifica se o usuário responsável existe.
        usuario = db.execute(
            text("""
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = :id_usuario
            """),
            {"id_usuario": dados.id_usuario_registro}
        ).first()

        if not usuario:
            raise LookupError("Usuário responsável não encontrado.")

        # Verifica se o caso existe e pertence ao assistido.
        if dados.id_caso is not None:
            caso = db.execute(
                text("""
                    SELECT id_caso
                    FROM casos_juridicos
                    WHERE id_caso = :id_caso
                    AND id_assistido = :id_assistido
                """),
                {
                    "id_caso": dados.id_caso,
                    "id_assistido": dados.id_assistido
                }
            ).first()

            if not caso:
                raise ValueError(
                    "O caso informado não existe ou não pertence ao assistido."
                )

        try:
            atendimento = AtendimentoRepository.criar(db, dados)

            db.commit()
            db.refresh(atendimento)

            return atendimento

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível registrar o atendimento. "
                "Verifique os relacionamentos informados."
            )

        except Exception:
            db.rollback()
            raise
