
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.repositories.historico_caso_repository import (
    HistoricoCasoRepository
)


class HistoricoCasoService:

    @staticmethod
    def listar(db: Session):
        return HistoricoCasoRepository.listar(db)

    @staticmethod
    def buscar_por_id(db: Session, id_historico: int):
        historico = HistoricoCasoRepository.buscar_por_id(
            db, id_historico
        )

        if not historico:
            raise LookupError(
                "Registro histórico não encontrado."
            )

        return historico

    @staticmethod
    def listar_por_caso(db: Session, id_caso: int):
        return HistoricoCasoRepository.listar_por_caso(
            db, id_caso
        )

    @staticmethod
    def listar_por_usuario(
        db: Session,
        id_usuario_responsavel: int
    ):
        return HistoricoCasoRepository.listar_por_usuario(
            db, id_usuario_responsavel
        )

    @staticmethod
    def _validar_relacionamentos(
        db: Session,
        id_caso: int,
        id_usuario_responsavel: int
    ):
        caso_existe = db.execute(
            text("""
                SELECT id_caso
                FROM casos_juridicos
                WHERE id_caso = :id_caso
            """),
            {"id_caso": id_caso}
        ).first()

        if not caso_existe:
            raise ValueError(
                "O caso jurídico informado não existe."
            )

        usuario_existe = db.execute(
            text("""
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = :id_usuario
            """),
            {"id_usuario": id_usuario_responsavel}
        ).first()

        if not usuario_existe:
            raise ValueError(
                "O usuário responsável informado não existe."
            )

    @staticmethod
    def criar(db: Session, dados):
        HistoricoCasoService._validar_relacionamentos(
            db,
            dados.id_caso,
            dados.id_usuario_responsavel
        )

        dados_historico = dados.model_dump()

        return HistoricoCasoRepository.criar(
            db,
            dados_historico
        )

