
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.documento_repository import DocumentoRepository
from app.models.usuario import Usuario


class DocumentoService:

    @staticmethod
    def _buscar_id_aluno(db: Session, id_usuario: int):
        resultado = db.execute(
            text("""
                SELECT id_aluno
                FROM alunos
                WHERE id_usuario = :id_usuario
            """),
            {"id_usuario": id_usuario}
        ).first()

        return resultado.id_aluno if resultado else None

    @staticmethod
    def _buscar_id_professor(db: Session, id_usuario: int):
        resultado = db.execute(
            text("""
                SELECT id_professor
                FROM professores
                WHERE id_usuario = :id_usuario
                  AND situacao = 'Ativo'
            """),
            {"id_usuario": id_usuario}
        ).first()

        return resultado.id_professor if resultado else None

    @staticmethod
    def _buscar_documento_permitido(
        db: Session,
        id_documento: int,
        usuario: Usuario
    ):
        if usuario.perfil == "Gestão":
            return DocumentoRepository.buscar_por_id(
                db, id_documento
            )

        if usuario.perfil == "Aluno":
            id_aluno = DocumentoService._buscar_id_aluno(
                db, usuario.id_usuario
            )

            if not id_aluno:
                return None

            return DocumentoRepository.buscar_por_id_e_aluno(
                db, id_documento, id_aluno
            )

        if usuario.perfil == "Professor":
            id_professor = DocumentoService._buscar_id_professor(
                db, usuario.id_usuario
            )

            if not id_professor:
                return None

            return DocumentoRepository.buscar_por_id_e_professor(
                db, id_documento, id_professor
            )

        raise PermissionError(
            "Perfil sem permissão para acessar documentos."
        )

    @staticmethod
    def listar(db: Session, usuario: Usuario):
        if usuario.perfil == "Gestão":
            return DocumentoRepository.listar(db)

        if usuario.perfil == "Aluno":
            id_aluno = DocumentoService._buscar_id_aluno(
                db, usuario.id_usuario
            )

            if not id_aluno:
                return []

            return DocumentoRepository.listar_por_aluno(
                db, id_aluno
            )

        if usuario.perfil == "Professor":
            id_professor = DocumentoService._buscar_id_professor(
                db, usuario.id_usuario
            )

            if not id_professor:
                return []

            return DocumentoRepository.listar_por_professor(
                db, id_professor
            )

        raise PermissionError(
            "Perfil sem permissão para consultar documentos."
        )

    @staticmethod
    def buscar_por_id(
        db: Session,
        id_documento: int,
        usuario: Usuario
    ):
        documento = DocumentoService._buscar_documento_permitido(
            db, id_documento, usuario
        )

        if not documento:
            raise LookupError("Documento não encontrado.")

        return documento

    @staticmethod
    def listar_por_caso(
        db: Session,
        id_caso: int,
        usuario: Usuario
    ):
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

        documentos = DocumentoService.listar(db, usuario)

        return [
            documento
            for documento in documentos
            if documento.id_caso == id_caso
        ]

    @staticmethod
    def listar_por_atendimento(
        db: Session,
        id_atendimento: int,
        usuario: Usuario
    ):
        atendimento = db.execute(
            text("""
                SELECT id_atendimento, id_caso
                FROM atendimentos
                WHERE id_atendimento = :id
            """),
            {"id": id_atendimento}
        ).first()

        if not atendimento:
            raise LookupError("Atendimento não encontrado.")

        if atendimento.id_caso is None:
            if usuario.perfil == "Gestão":
                return DocumentoRepository.listar_por_atendimento(
                    db, id_atendimento
                )

            return []

        documentos = DocumentoService.listar(db, usuario)

        return [
            documento
            for documento in documentos
            if documento.id_atendimento == id_atendimento
        ]

    @staticmethod
    def criar(
        db: Session,
        dados,
        usuario: Usuario
    ):
        if usuario.perfil not in ("Aluno", "Gestão"):
            raise PermissionError(
                "Somente alunos e Gestão podem cadastrar documentos."
            )

        dados_documento = dados.model_dump(exclude={"id_usuario_inclusao"})

        id_caso = dados_documento.get("id_caso")
        id_atendimento = dados_documento.get("id_atendimento")

        if id_caso is None and id_atendimento is None:
            raise ValueError(
                "O documento deve estar vinculado a um caso jurídico "
                "ou a um atendimento."
            )

        # Valida o caso jurídico.
        caso = None

        if id_caso is not None:
            caso = db.execute(
                text("""
                    SELECT id_caso, id_aluno_responsavel
                    FROM casos_juridicos
                    WHERE id_caso = :id
                """),
                {"id": id_caso}
            ).first()

            if not caso:
                raise LookupError("Caso jurídico não encontrado.")

        # Valida o atendimento.
        atendimento = None

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

        # Confere a compatibilidade entre os vínculos.
        if (
            caso is not None
            and atendimento is not None
            and atendimento.id_caso != id_caso
        ):
            raise ValueError(
                "O atendimento informado não pertence ao caso jurídico indicado."
            )

        # O aluno só pode cadastrar documentos em seus próprios casos.
        if usuario.perfil == "Aluno":
            id_aluno = DocumentoService._buscar_id_aluno(
                db, usuario.id_usuario
            )

            if not id_aluno:
                raise PermissionError(
                    "O usuário não possui cadastro de aluno ativo."
                )

            id_caso_validado = id_caso

            if id_caso_validado is None and atendimento is not None:
                id_caso_validado = atendimento.id_caso

            if id_caso_validado is None:
                raise PermissionError(
                    "Não é permitido cadastrar documentos em atendimentos "
                    "sem vínculo com um caso jurídico."
                )

            caso_aluno = db.execute(
                text("""
                    SELECT id_caso
                    FROM casos_juridicos
                    WHERE id_caso = :id_caso
                      AND id_aluno_responsavel = :id_aluno
                """),
                {
                    "id_caso": id_caso_validado,
                    "id_aluno": id_aluno
                }
            ).first()

            if not caso_aluno:
                raise PermissionError(
                    "Você só pode cadastrar documentos nos seus próprios casos."
                )

        # O usuário autenticado é sempre o responsável pela inclusão.
        dados_documento["id_usuario_inclusao"] = usuario.id_usuario

        try:
            return DocumentoRepository.criar(
                db, dados_documento
            )

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível cadastrar o documento. "
                "Verifique os vínculos informados."
            )

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def atualizar(
        db: Session,
        id_documento: int,
        dados,
        usuario: Usuario
    ):
        documento = DocumentoService._buscar_documento_permitido(
            db, id_documento, usuario
        )

        if not documento:
            raise LookupError("Documento não encontrado.")

        if usuario.perfil != "Gestão":
            raise PermissionError(
                "Somente Gestão pode atualizar documentos."
            )

        dados_atualizacao = dados.model_dump(
            exclude_unset=True,
            exclude_none=True
        )

        # Impede a alteração do usuário responsável pela inclusão.
        dados_atualizacao.pop("id_usuario_inclusao", None)

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

            if (
                id_caso_final is not None
                and atendimento.id_caso != id_caso_final
            ):
                raise ValueError(
                    "O atendimento informado não pertence ao caso jurídico indicado."
                )

        try:
            return DocumentoRepository.atualizar(
                db, documento, dados_atualizacao
            )

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível atualizar o documento."
            )

        except Exception:
            db.rollback()
            raise
