
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from app.repositories.atividade import AtividadeRepository
from app.schemas.atividade import AtividadeCreate, AtividadeUpdate
from app.models.usuario import Usuario
from app.models.historico_caso import HistoricoCaso


class AtividadeService:

    # Registra uma ocorrência no histórico do caso relacionado à atividade.
    @staticmethod
    def _registrar_historico(
        db: Session,
        id_caso: int,
        usuario: Usuario,
        tipo_ocorrencia: str,
        descricao: str,
        id_atividade: int
    ):
        historico = HistoricoCaso(
            id_caso=id_caso,
            id_usuario_responsavel=usuario.id_usuario,
            tipo_ocorrencia=tipo_ocorrencia,
            descricao=descricao,
            referencia_registro_afetado=f"Atividade #{id_atividade}"
        )

        db.add(historico)

    # Busca o identificador do cadastro de aluno vinculado ao usuário.
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

    # Busca o identificador do professor, considerando somente cadastros ativos.
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

    # Busca uma atividade somente quando o usuário possui acesso a ela.
    @staticmethod
    def _buscar_atividade_permitida(
        db: Session,
        id_atividade: int,
        usuario: Usuario
    ):
        if usuario.perfil == "Gestão":
            return AtividadeRepository.buscar_por_id(
                db, id_atividade
            )

        if usuario.perfil == "Aluno":
            id_aluno = AtividadeService._buscar_id_aluno(
                db, usuario.id_usuario
            )

            if not id_aluno:
                return None

            return AtividadeRepository.buscar_por_id_e_aluno(
                db, id_atividade, id_aluno
            )

        if usuario.perfil == "Professor":
            id_professor = AtividadeService._buscar_id_professor(
                db, usuario.id_usuario
            )

            if not id_professor:
                return None

            return AtividadeRepository.buscar_por_id_e_professor(
                db, id_atividade, id_professor
            )

        raise PermissionError(
            "Perfil sem permissão para acessar atividades."
        )

    # Lista as atividades conforme o perfil e os vínculos do usuário.
    @staticmethod
    def listar(db: Session, usuario: Usuario):
        if usuario.perfil == "Gestão":
            return AtividadeRepository.listar(db)

        if usuario.perfil == "Aluno":
            id_aluno = AtividadeService._buscar_id_aluno(
                db, usuario.id_usuario
            )

            if not id_aluno:
                return []

            return AtividadeRepository.listar_por_aluno(
                db, id_aluno
            )

        if usuario.perfil == "Professor":
            id_professor = AtividadeService._buscar_id_professor(
                db, usuario.id_usuario
            )

            if not id_professor:
                return []

            return AtividadeRepository.listar_por_professor(
                db, id_professor
            )

        raise PermissionError(
            "Perfil sem permissão para consultar atividades."
        )

    # Busca uma atividade individual respeitando as permissões do usuário.
    @staticmethod
    def buscar_por_id(
        db: Session,
        id_atividade: int,
        usuario: Usuario
    ):
        atividade = AtividadeService._buscar_atividade_permitida(
            db, id_atividade, usuario
        )

        if not atividade:
            raise LookupError("Atividade não encontrada.")

        return atividade

    # Lista as atividades de um caso, respeitando o acesso de cada perfil.
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
                WHERE id_caso = :id_caso
            """),
            {"id_caso": id_caso}
        ).first()

        if not caso:
            raise LookupError("Caso jurídico não encontrado.")

        if usuario.perfil == "Gestão":
            return AtividadeRepository.listar_por_caso(
                db, id_caso
            )

        atividades = AtividadeService.listar(db, usuario)

        return [
            atividade
            for atividade in atividades
            if atividade.id_caso == id_caso
        ]

    # Lista as atividades de um responsável conforme as permissões do usuário.
    @staticmethod
    def listar_por_responsavel(
        db: Session,
        id_responsavel: int,
        usuario: Usuario
    ):
        if usuario.perfil == "Gestão":
            return AtividadeRepository.listar_por_responsavel(
                db, id_responsavel
            )

        if usuario.perfil == "Aluno":
            if id_responsavel != usuario.id_usuario:
                raise PermissionError(
                    "Você só pode consultar suas próprias atividades."
                )

        atividades = AtividadeService.listar(db, usuario)

        return [
            atividade
            for atividade in atividades
            if atividade.id_responsavel == id_responsavel
        ]

    # Cadastra uma atividade após validar o caso, as permissões e o responsável.
    @staticmethod
    def criar(
        db: Session,
        dados: AtividadeCreate,
        usuario: Usuario
    ):
        if usuario.perfil not in ("Aluno", "Professor", "Gestão"):
            raise PermissionError(
                "Somente Alunos, Professores e Gestão "
                "podem cadastrar atividades."
            )

        caso = db.execute(
            text("""
                SELECT id_caso,
                       id_aluno_responsavel,
                       id_professor_orientador,
                       situacao
                FROM casos_juridicos
                WHERE id_caso = :id_caso
            """),
            {"id_caso": dados.id_caso}
        ).first()

        if not caso:
            raise LookupError("Caso jurídico não encontrado.")

        # RN13: impede o cadastro de atividades em casos encerrados.
        if caso.situacao == "Encerrado":
            raise ValueError(
                "Não é permitido cadastrar novas atividades "
                "em casos encerrados."
            )

        if usuario.perfil == "Aluno":
            id_aluno = AtividadeService._buscar_id_aluno(
                db, usuario.id_usuario
            )

            if not id_aluno or caso.id_aluno_responsavel != id_aluno:
                raise PermissionError(
                    "Você só pode cadastrar atividades nos seus próprios casos."
                )

        elif usuario.perfil == "Professor":
            id_professor = AtividadeService._buscar_id_professor(
                db, usuario.id_usuario
            )

            if (
                not id_professor
                or caso.id_professor_orientador != id_professor
            ):
                raise PermissionError(
                    "Você só pode cadastrar atividades em casos "
                    "sob sua orientação."
                )

        # RN14: exige que o caso possua um aluno responsável.
        if not caso.id_aluno_responsavel:
            raise ValueError(
                "O caso precisa ter um aluno responsável antes "
                "do cadastro de atividades."
            )

        responsavel = db.execute(
            text("""
                SELECT u.id_usuario
                FROM alunos a
                JOIN usuarios u ON u.id_usuario = a.id_usuario
                WHERE a.id_aluno = :id_aluno
                  AND u.situacao_conta = 'Ativo'
            """),
            {"id_aluno": caso.id_aluno_responsavel}
        ).first()

        if not responsavel:
            raise LookupError(
                "O aluno responsável pelo caso não foi encontrado "
                "ou está inativo."
            )

        id_responsavel_esperado = responsavel.id_usuario

        # RN14: rejeita um responsável diferente do aluno do caso.
        if (
            dados.id_responsavel is not None
            and dados.id_responsavel != id_responsavel_esperado
        ):
            raise ValueError(
                "A atividade deve ser atribuída ao aluno "
                "responsável pelo caso."
            )

        dados_atividade = dados.model_copy(
            update={
                "id_responsavel": id_responsavel_esperado
            }
        )

        # Define automaticamente a data quando a atividade já nasce concluída.
        if dados.situacao == "Concluída":
            data_conclusao = datetime.now()
        else:
            data_conclusao = None

        try:
            atividade = AtividadeRepository.criar(
                db, dados_atividade
            )

            if data_conclusao:
                atividade.data_conclusao = data_conclusao

            db.flush()

            AtividadeService._registrar_historico(
                db,
                atividade.id_caso,
                usuario,
                "Cadastro de atividade",
                f"{usuario.perfil} cadastrou a atividade "
                f"'{atividade.titulo}'.",
                atividade.id_atividade
            )

            db.commit()
            db.refresh(atividade)

            return atividade

        # Desfaz a transação diante de violações de integridade.
        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível cadastrar a atividade. "
                "Verifique os dados e os vínculos informados."
            )

        # Desfaz a transação diante de qualquer outro erro inesperado.
        except Exception:
            db.rollback()
            raise

    # Atualiza uma atividade, validando permissões, vínculos e regras de negócio.
    @staticmethod
    def atualizar(
        db: Session,
        id_atividade: int,
        dados: AtividadeUpdate,
        usuario: Usuario
    ):
        atividade = AtividadeService._buscar_atividade_permitida(
            db, id_atividade, usuario
        )

        if not atividade:
            raise LookupError("Atividade não encontrada.")

        # Obtém somente os campos enviados na solicitação.
        dados_atualizacao = dados.model_dump(
            exclude_unset=True,
            exclude_none=True
        )

        # Guarda os valores anteriores para identificar alterações no histórico.
        dados_anteriores = {
            campo: getattr(atividade, campo)
            for campo in dados_atualizacao
        }

        if usuario.perfil == "Aluno":
            if "id_responsavel" in dados_atualizacao:
                raise PermissionError(
                    "O aluno não pode alterar o responsável pela atividade."
                )

        if usuario.perfil == "Professor":
            if "id_responsavel" in dados_atualizacao:
                raise PermissionError(
                    "O professor não pode alterar o responsável pela atividade."
                )

        if "id_caso" in dados_atualizacao:
            caso = db.execute(
                text("""
                    SELECT id_caso, id_aluno_responsavel,
                           id_professor_orientador
                    FROM casos_juridicos
                    WHERE id_caso = :id_caso
                """),
                {"id_caso": dados_atualizacao["id_caso"]}
            ).first()

            if not caso:
                raise LookupError("Caso jurídico não encontrado.")

            if usuario.perfil == "Aluno":
                id_aluno = AtividadeService._buscar_id_aluno(
                    db, usuario.id_usuario
                )

                if not id_aluno or caso.id_aluno_responsavel != id_aluno:
                    raise PermissionError(
                        "Você não pode transferir a atividade para outro caso."
                    )

            if usuario.perfil == "Professor":
                id_professor = AtividadeService._buscar_id_professor(
                    db, usuario.id_usuario
                )

                if (
                    not id_professor
                    or caso.id_professor_orientador != id_professor
                ):
                    raise PermissionError(
                        "Você não pode transferir a atividade para um caso "
                        "que não está sob sua orientação."
                    )

        # RN14: identifica o aluno responsável pelo caso de destino.
        id_caso_destino = dados_atualizacao.get(
            "id_caso", atividade.id_caso
        )

        caso_destino = db.execute(
            text("""
                SELECT id_aluno_responsavel
                FROM casos_juridicos
                WHERE id_caso = :id_caso
            """),
            {"id_caso": id_caso_destino}
        ).first()

        if not caso_destino:
            raise LookupError("Caso jurídico não encontrado.")

        if not caso_destino.id_aluno_responsavel:
            raise ValueError(
                "O caso precisa ter um aluno responsável."
            )

        responsavel = db.execute(
            text("""
                SELECT u.id_usuario
                FROM alunos a
                JOIN usuarios u ON u.id_usuario = a.id_usuario
                WHERE a.id_aluno = :id_aluno
                  AND u.situacao_conta = 'Ativo'
            """),
            {"id_aluno": caso_destino.id_aluno_responsavel}
        ).first()

        if not responsavel:
            raise LookupError(
                "O aluno responsável pelo caso não foi encontrado "
                "ou está inativo."
            )

        id_responsavel_esperado = responsavel.id_usuario

        # Rejeita a alteração manual para um responsável diferente do aluno do caso.
        if "id_responsavel" in dados_atualizacao:
            if (
                dados_atualizacao["id_responsavel"]
                != id_responsavel_esperado
            ):
                raise ValueError(
                    "A atividade deve ser atribuída ao aluno "
                    "responsável pelo caso."
                )

        # Guarda o responsável anterior, inclusive quando a mudança é automática.
        dados_anteriores.setdefault(
            "id_responsavel",
            atividade.id_responsavel
        )

        # Ajusta o responsável ao aluno vinculado ao caso de destino.
        dados_atualizacao["id_responsavel"] = id_responsavel_esperado

        # Preenche a data de conclusão automaticamente quando necessário.
        if dados_atualizacao.get("situacao") == "Concluída":
            if not atividade.data_conclusao:
                dados_atualizacao["data_conclusao"] = datetime.now()

            # Inclui a data anterior na comparação do histórico.
            dados_anteriores["data_conclusao"] = atividade.data_conclusao

        try:
            atividade = AtividadeRepository.atualizar(
                db,
                atividade,
                dados_atualizacao
            )

            # Compara os valores anteriores e atuais para identificar alterações.
            alteracoes = []

            for campo, valor_anterior in dados_anteriores.items():
                valor_novo = getattr(atividade, campo)

                if valor_anterior != valor_novo:
                    alteracoes.append(
                        f"{campo}: '{valor_anterior}' para '{valor_novo}'"
                    )

            # Registra no histórico somente quando houve alteração efetiva.
            if alteracoes:
                descricao_historico = (
                    f"A atividade '{atividade.titulo}' foi atualizada. "
                    f"Alterações: {'; '.join(alteracoes)}"
                )

                AtividadeService._registrar_historico(
                    db,
                    atividade.id_caso,
                    usuario,
                    "Atualização de atividade",
                    descricao_historico,
                    atividade.id_atividade
                )

            db.commit()
            db.refresh(atividade)

            return atividade

        # Desfaz a transação diante de violações de integridade.
        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível atualizar a atividade."
            )

        # Desfaz a transação diante de qualquer outro erro inesperado.
        except Exception:
            db.rollback()
            raise
