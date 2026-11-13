
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.repositories.documento_repository import DocumentoRepository


class DocumentoService:

    @staticmethod
    def listar(db: Session):
        return DocumentoRepository.listar(db)

    @staticmethod
    def buscar_por_id(db: Session, id_documento: int):
        documento = DocumentoRepository.buscar_por_id(
            db, id_documento
        )

        if not documento:
            raise LookupError("Documento não encontrado.")

        return documento

    @staticmethod
    def listar_por_caso(db: Session, id_caso: int):
        caso = db.execute(
            text("""
                SELECT id_caso
                FROM casos_juridicos
                WHERE id_caso = :id
            """),
            {"id": id_caso}
        ).first()

        if not caso:
            raise LookupError("Caso jurídico não encontrado.")

        return DocumentoRepository.listar_por_caso(db, id_caso)

    @staticmethod
    def listar_por_atendimento(db: Session, id_atendimento: int):
        atendimento = db.execute(
            text("""
                SELECT id_atendimento
                FROM atendimentos
                WHERE id_atendimento = :id
            """),
            {"id": id_atendimento}
        ).first()

        if not atendimento:
            raise LookupError("Atendimento não encontrado.")

        return DocumentoRepository.listar_por_atendimento(
            db, id_atendimento
        )

    @staticmethod
    def criar(db: Session, dados):
        dados_documento = dados.model_dump()

        id_caso = dados_documento.get("id_caso")
        id_atendimento = dados_documento.get("id_atendimento")
        id_usuario = dados_documento["id_usuario_inclusao"]

        # Verifica se o usuário responsável pela inclusão existe.
        usuario = db.execute(
            text("""
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = :id
            """),
            {"id": id_usuario}
        ).first()

        if not usuario:
            raise LookupError("Usuário responsável não encontrado.")

        # Verifica se o caso informado existe.
        if id_caso is not None:
            caso = db.execute(
                text("""
                    SELECT id_caso
                    FROM casos_juridicos
                    WHERE id_caso = :id
                """),
                {"id": id_caso}
            ).first()

            if not caso:
                raise LookupError("Caso jurídico não encontrado.")

        # Verifica se o atendimento informado existe.
        if id_atendimento is not None:
            atendimento = db.execute(
                text("""
                    SELECT id_atendimento, id_caso, id_assistido
                    FROM atendimentos
                    WHERE id_atendimento = :id
                """),
                {"id": id_atendimento}
            ).first()

            if not atendimento:
                raise LookupError("Atendimento não encontrado.")

            # Quando ambos são informados, devem pertencer ao mesmo caso.
            if id_caso is not None:
                if atendimento.id_caso != id_caso:
                    raise ValueError(
                        "O atendimento informado não pertence ao caso jurídico indicado."
                    )

        return DocumentoRepository.criar(db, dados_documento)

    @staticmethod
    def atualizar(db: Session, id_documento: int, dados):
        documento = DocumentoRepository.buscar_por_id(
            db, id_documento
        )

        if not documento:
            raise LookupError("Documento não encontrado.")

        dados_atualizacao = dados.model_dump(exclude_unset=True)

        # Calcula os vínculos que permanecerão após a atualização.
        id_caso_final = dados_atualizacao.get(
            "id_caso", documento.id_caso
        )
        id_atendimento_final = dados_atualizacao.get(
            "id_atendimento", documento.id_atendimento
        )

        if id_caso_final is None and id_atendimento_final is None:
            raise ValueError(
                "O documento deve permanecer vinculado a um caso jurídico "
                "ou a um atendimento."
            )

        # Valida a existência do caso, se informado.
        if id_caso_final is not None:
            caso = db.execute(
                text("""
                    SELECT id_caso
                    FROM casos_juridicos
                    WHERE id_caso = :id
                """),
                {"id": id_caso_final}
            ).first()

            if not caso:
                raise LookupError("Caso jurídico não encontrado.")

        # Valida o atendimento e a compatibilidade entre os vínculos.
        if id_atendimento_final is not None:
            atendimento = db.execute(
                text("""
                    SELECT id_atendimento, id_caso
                    FROM atendimentos
                    WHERE id_atendimento = :id
                """),
                {"id": id_atendimento_final}
            ).first()

            if not atendimento:
                raise LookupError("Atendimento não encontrado.")

            if id_caso_final is not None:
                if atendimento.id_caso != id_caso_final:
                    raise ValueError(
                        "O atendimento informado não pertence ao caso jurídico indicado."
                    )

        return DocumentoRepository.atualizar(
            db, documento, dados_atualizacao
        )
