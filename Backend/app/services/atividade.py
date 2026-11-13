
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from app.repositories.atividade import AtividadeRepository
from app.schemas.atividade import AtividadeCreate, AtividadeUpdate


class AtividadeService:

    @staticmethod
    def listar(db: Session):
        return AtividadeRepository.listar(db)

    @staticmethod
    def buscar_por_id(db: Session, id_atividade: int):
        atividade = AtividadeRepository.buscar_por_id(
            db, id_atividade
        )

        if not atividade:
            raise LookupError("Atividade não encontrada.")

        return atividade

    @staticmethod
    def listar_por_caso(db: Session, id_caso: int):

        caso = db.execute(
            text("""
                SELECT id_caso
                FROM casos_juridicos
                WHERE id_caso = :id_caso
            """),
            {"id_caso": id_caso}
        ).first()

        if not caso:
            raise LookupError("Caso jurídico não encontrado.")

        return AtividadeRepository.listar_por_caso(
            db, id_caso
        )

    @staticmethod
    def listar_por_responsavel(db: Session, id_responsavel: int):

        usuario = db.execute(
            text("""
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = :id_usuario
            """),
            {"id_usuario": id_responsavel}
        ).first()

        if not usuario:
            raise LookupError("Usuário responsável não encontrado.")

        return AtividadeRepository.listar_por_responsavel(
            db, id_responsavel
        )

    @staticmethod
    def criar(db: Session, dados: AtividadeCreate):

        # Verifica se o caso jurídico existe
        caso = db.execute(
            text("""
                SELECT id_caso
                FROM casos_juridicos
                WHERE id_caso = :id_caso
            """),
            {"id_caso": dados.id_caso}
        ).first()

        if not caso:
            raise LookupError("Caso jurídico não encontrado.")

        # Verifica se o usuário responsável existe
        usuario = db.execute(
            text("""
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = :id_usuario
            """),
            {"id_usuario": dados.id_responsavel}
        ).first()

        if not usuario:
            raise LookupError("Usuário responsável não encontrado.")

        dados_atividade = dados.model_dump()

        # Registra a data de conclusão caso já seja criada como concluída
        if dados.situacao == "Concluída":
            dados_atividade["data_conclusao"] = datetime.now()

        try:
            atividade = AtividadeRepository.criar(
                db,
                dados
            )

            if dados.situacao == "Concluída":
                atividade.data_conclusao = dados_atividade["data_conclusao"]

            db.commit()
            db.refresh(atividade)

            return atividade

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível cadastrar a atividade. "
                "Verifique os dados e os vínculos informados."
            )

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def atualizar(
        db: Session,
        id_atividade: int,
        dados: AtividadeUpdate
    ):

        atividade = AtividadeRepository.buscar_por_id(
            db, id_atividade
        )

        if not atividade:
            raise LookupError("Atividade não encontrada.")

        dados_atualizacao = dados.model_dump(
            exclude_unset=True,
            exclude_none=True
        )

        # Valida o caso jurídico caso ele seja alterado
        if "id_caso" in dados_atualizacao:

            caso = db.execute(
                text("""
                    SELECT id_caso
                    FROM casos_juridicos
                    WHERE id_caso = :id_caso
                """),
                {"id_caso": dados_atualizacao["id_caso"]}
            ).first()

            if not caso:
                raise LookupError("Caso jurídico não encontrado.")

        # Valida o usuário responsável caso ele seja alterado
        if "id_responsavel" in dados_atualizacao:

            usuario = db.execute(
                text("""
                    SELECT id_usuario
                    FROM usuarios
                    WHERE id_usuario = :id_usuario
                """),
                {"id_usuario": dados_atualizacao["id_responsavel"]}
            ).first()

            if not usuario:
                raise LookupError("Usuário responsável não encontrado.")

        # Registra automaticamente a conclusão da atividade
        if dados_atualizacao.get("situacao") == "Concluída":
            if not atividade.data_conclusao:
                dados_atualizacao["data_conclusao"] = datetime.now()

        try:
            atividade = AtividadeRepository.atualizar(
                db,
                atividade,
                dados_atualizacao
            )

            db.commit()
            db.refresh(atividade)

            return atividade

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível atualizar a atividade."
            )

        except Exception:
            db.rollback()
            raise
