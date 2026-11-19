
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from app.repositories.atividade import AtividadeRepository
from app.schemas.atividade import AtividadeCreate, AtividadeUpdate
from app.models.usuario import Usuario
from app.models.historico_caso import HistoricoCaso


class AtividadeService:

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

        # RN13: impedir cadastro de atividades em casos encerrados.
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

        # RN14: a atividade deve pertencer ao aluno responsável pelo caso.
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

        # RN14: rejeitar responsável diferente do aluno vinculado ao caso.
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
        dados: AtividadeUpdate,
        usuario: Usuario
    ):
        atividade = AtividadeService._buscar_atividade_permitida(
            db, id_atividade, usuario
        )

        if not atividade:
            raise LookupError("Atividade não encontrada.")

        dados_atualizacao = dados.model_dump(
            exclude_unset=True,
            exclude_none=True
        )

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

        # RN14: a atividade deve permanecer atribuída
        # ao aluno responsável pelo caso.
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

        if "id_responsavel" in dados_atualizacao:
            if (
                dados_atualizacao["id_responsavel"]
                != id_responsavel_esperado
            ):
                raise ValueError(
                    "A atividade deve ser atribuída ao aluno "
                    "responsável pelo caso."
                )

        dados_atualizacao["id_responsavel"] = id_responsavel_esperado

        if dados_atualizacao.get("situacao") == "Concluída":
            if not atividade.data_conclusao:
                dados_atualizacao["data_conclusao"] = datetime.now()

            # Registrar também a data de conclusão automática
            # na comparação utilizada para gerar o históri    co.
            dados_anteriores["data_conclusao"] = atividade.data_conclusao


        try:
            atividade = AtividadeRepository.atualizar(
                db,
                atividade,
                dados_atualizacao
            )

            alteracoes = []

            for campo, valor_anterior in dados_anteriores.items():
                valor_novo = getattr(atividade, campo)

                if valor_anterior != valor_novo:
                    alteracoes.append(
                        f"{campo}: '{valor_anterior}' para '{valor_novo}'"
                    )

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

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível atualizar a atividade."
            )

        except Exception:
            db.rollback()
            raise
