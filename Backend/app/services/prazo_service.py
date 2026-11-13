
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.repositories.prazo_repository import PrazoRepository


class PrazoService:

    @staticmethod
    def listar(db: Session):
        return PrazoRepository.listar(db)

    @staticmethod
    def buscar_por_id(db: Session, id_prazo: int):
        prazo = PrazoRepository.buscar_por_id(db, id_prazo)

        if not prazo:
            raise LookupError("Prazo não encontrado.")

        return prazo

    @staticmethod
    def listar_por_caso(db: Session, id_caso: int):
        return PrazoRepository.listar_por_caso(db, id_caso)

    @staticmethod
    def listar_por_responsavel(db: Session, id_responsavel: int):
        return PrazoRepository.listar_por_responsavel(
            db, id_responsavel
        )

    @staticmethod
    def _validar_relacionamentos(
        db: Session,
        id_caso: int,
        id_atividade: int | None,
        id_responsavel: int
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
                WHERE id_usuario = :id_responsavel
            """),
            {"id_responsavel": id_responsavel}
        ).first()

        if not usuario_existe:
            raise ValueError(
                "O usuário responsável não existe."
            )

        if id_atividade is not None:
            atividade_existe = db.execute(
                text("""
                    SELECT id_atividade
                    FROM atividades
                    WHERE id_atividade = :id_atividade
                      AND id_caso = :id_caso
                """),
                {
                    "id_atividade": id_atividade,
                    "id_caso": id_caso
                }
            ).first()

            if not atividade_existe:
                raise ValueError(
                    "A atividade informada não existe ou "
                    "não pertence ao caso selecionado."
                )

    @staticmethod
    def criar(db: Session, dados):
        PrazoService._validar_relacionamentos(
            db,
            dados.id_caso,
            dados.id_atividade,
            dados.id_responsavel
        )

        dados_prazo = dados.model_dump()

        if dados.situacao == "Concluído":
            dados_prazo["data_conclusao"] = datetime.now()

        return PrazoRepository.criar(db, dados_prazo)

    @staticmethod
    def atualizar(
        db: Session,
        id_prazo: int,
        dados
    ):
        prazo = PrazoService.buscar_por_id(db, id_prazo)

        dados_atualizacao = dados.model_dump(
            exclude_unset=True
        )

        id_caso = dados_atualizacao.get(
            "id_caso", prazo.id_caso
        )

        id_atividade = dados_atualizacao.get(
            "id_atividade", prazo.id_atividade
        )

        id_responsavel = dados_atualizacao.get(
            "id_responsavel", prazo.id_responsavel
        )

        PrazoService._validar_relacionamentos(
            db,
            id_caso,
            id_atividade,
            id_responsavel
        )

        nova_situacao = dados_atualizacao.get(
            "situacao", prazo.situacao
        )

        if nova_situacao == "Concluído":
            if prazo.situacao != "Concluído":
                dados_atualizacao["data_conclusao"] = datetime.now()

        elif "situacao" in dados_atualizacao:
            dados_atualizacao["data_conclusao"] = None

        return PrazoRepository.atualizar(
            db,
            prazo,
            dados_atualizacao
        )
