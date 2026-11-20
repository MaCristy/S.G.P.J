
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.documento_repository import DocumentoRepository
from app.models.usuario import Usuario


class DocumentoService:

    # Busca o cadastro acadêmico do aluno associado ao usuário.
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

    # Busca o cadastro ativo do professor associado ao usuário.
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

    # Localiza um documento respeitando as permissões de cada perfil.
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

    # Lista os documentos que o usuário autenticado tem permissão para visualizar.
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

    # Busca um documento específico e verifica se o usuário pode acessá-lo.
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

    # Lista os documentos associados a um caso jurídico.
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

    # Lista os documentos associados a um atendimento.
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

        # Permite que a Gestão consulte documentos de atendimentos sem caso vinculado.
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

    # Cadastra um documento e valida seus vínculos e permissões.
    @staticmethod
    def criar(
        db: Session,
        dados,
        usuario: Usuario
    ):
        # Somente Aluno e Gestão podem cadastrar documentos.
        if usuario.perfil not in ("Aluno", "Gestão"):
            raise PermissionError(
                "Somente alunos e Gestão podem cadastrar documentos."
            )

        dados_documento = dados.model_dump(exclude={"id_usuario_inclusao"})

        id_caso = dados_documento.get("id_caso")
        id_atendimento = dados_documento.get("id_atendimento")

        # Exige pelo menos um vínculo para o documento.
        if id_caso is None and id_atendimento is None:
            raise ValueError(
                "O documento deve estar vinculado a um caso jurídico "
                "ou a um atendimento."
            )

        # Valida a existência do caso jurídico informado.
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

        # Valida a existência do atendimento informado.
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

        # Garante que o atendimento pertença ao caso informado.
        if (
            caso is not None
            and atendimento is not None
            and atendimento.id_caso != id_caso
        ):
            raise ValueError(
                "O atendimento informado não pertence ao caso jurídico indicado."
            )

        # O aluno só pode cadastrar documentos em casos sob sua responsabilidade.
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

        # Define o usuário autenticado como responsável pela inclusão.
        dados_documento["id_usuario_inclusao"] = usuario.id_usuario

        try:
            return DocumentoRepository.criar(
                db, dados_documento
            )

        # Trata erros de integridade relacionados aos vínculos no banco.
        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível cadastrar o documento. "
                "Verifique os vínculos informados."
            )

        # Desfaz a transação caso ocorra qualquer outro erro.
        except Exception:
            db.rollback()
            raise

    # Atualiza os dados de um documento, permitindo alterar seus vínculos.
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

        # Somente Gestão possui permissão para atualizar documentos.
        if usuario.perfil != "Gestão":
            raise PermissionError(
                "Somente Gestão pode atualizar documentos."
            )

        # Preserva os campos não enviados e permite limpar vínculos com null.
        dados_atualizacao = dados.model_dump(
            exclude_unset=True
        )

        # Impede a alteração do usuário responsável pela inclusão.
        dados_atualizacao.pop("id_usuario_inclusao", None)

        id_caso_final = dados_atualizacao.get(
            "id_caso", documento.id_caso
        )
        id_atendimento_final = dados_atualizacao.get(
            "id_atendimento", documento.id_atendimento
        )

        # Impede que o documento fique sem vínculo com caso ou atendimento.
        if id_caso_final is None and id_atendimento_final is None:
            raise ValueError(
                "O documento deve permanecer vinculado a um caso jurídico "
                "ou a um atendimento."
            )

        # Verifica se o caso informado existe.
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

        # Verifica se o atendimento existe e pertence ao caso informado.
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

        # Trata erros de integridade durante a atualização.
        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível atualizar o documento."
            )

        # Desfaz a transação caso ocorra qualquer outro erro.
        except Exception:
            db.rollback()
            raise
