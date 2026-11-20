
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.usuario import Usuario
from app.models.prazo import Prazo
from app.models.historico_caso import HistoricoCaso

from app.repositories.prazo_repository import PrazoRepository


class PrazoService:

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

    # Busca os dados do caso necessários para validar os vínculos e permissões.
    @staticmethod
    def _buscar_caso(db: Session, id_caso: int):
        return db.execute(
            text("""
                SELECT
                    id_caso,
                    id_aluno_responsavel,
                    id_professor_orientador
                FROM casos_juridicos
                WHERE id_caso = :id_caso
            """),
            {"id_caso": id_caso}
        ).first()

    # Registra no histórico do caso uma ocorrência relacionada ao prazo.
    @staticmethod
    def _registrar_historico(
        db: Session,
        id_caso: int,
        usuario: Usuario,
        tipo_ocorrencia: str,
        descricao: str,
        id_prazo: int
    ):
        historico = HistoricoCaso(
            id_caso=id_caso,
            id_usuario_responsavel=usuario.id_usuario,
            tipo_ocorrencia=tipo_ocorrencia,
            descricao=descricao,
            referencia_registro_afetado=f"Prazo #{id_prazo}"
        )

        db.add(historico)

    # Busca um prazo respeitando as permissões de cada perfil.
    @staticmethod
    def _buscar_prazo_permitido(
        db: Session,
        id_prazo: int,
        usuario: Usuario
    ):
        if usuario.perfil == "Gestão":
            return PrazoRepository.buscar_por_id(
                db, id_prazo
            )

        if usuario.perfil == "Aluno":
            id_aluno = PrazoService._buscar_id_aluno(
                db, usuario.id_usuario
            )

            if not id_aluno:
                return None

            return PrazoRepository.buscar_por_id_e_aluno(
                db, id_prazo, id_aluno
            )

        if usuario.perfil == "Professor":
            id_professor = PrazoService._buscar_id_professor(
                db, usuario.id_usuario
            )

            if not id_professor:
                return None

            return PrazoRepository.buscar_por_id_e_professor(
                db, id_prazo, id_professor
            )

        raise PermissionError(
            "Perfil sem permissão para acessar prazos."
        )

    # Lista os prazos que o usuário autenticado tem permissão para consultar.
    @staticmethod
    def listar(db: Session, usuario: Usuario):
        if usuario.perfil == "Gestão":
            return PrazoRepository.listar(db)

        if usuario.perfil == "Aluno":
            id_aluno = PrazoService._buscar_id_aluno(
                db, usuario.id_usuario
            )

            if not id_aluno:
                return []

            return PrazoRepository.listar_por_aluno(
                db, id_aluno
            )

        if usuario.perfil == "Professor":
            id_professor = PrazoService._buscar_id_professor(
                db, usuario.id_usuario
            )

            if not id_professor:
                return []

            return PrazoRepository.listar_por_professor(
                db, id_professor
            )

        raise PermissionError(
            "Perfil sem permissão para consultar prazos."
        )

    # Busca um prazo específico verificando se o usuário pode acessá-lo.
    @staticmethod
    def buscar_por_id(
        db: Session,
        id_prazo: int,
        usuario: Usuario
    ):
        prazo = PrazoService._buscar_prazo_permitido(
            db, id_prazo, usuario
        )

        if not prazo:
            raise LookupError("Prazo não encontrado.")

        return prazo

    # Lista os prazos associados a um caso jurídico.
    @staticmethod
    def listar_por_caso(
        db: Session,
        id_caso: int,
        usuario: Usuario
    ):
        caso = PrazoService._buscar_caso(
            db, id_caso
        )

        if not caso:
            raise LookupError(
                "Caso jurídico não encontrado."
            )

        prazos = PrazoService.listar(db, usuario)

        return [
            prazo for prazo in prazos
            if prazo.id_caso == id_caso
        ]

    # Lista os prazos de um responsável respeitando as permissões do perfil.
    @staticmethod
    def listar_por_responsavel(
        db: Session,
        id_responsavel: int,
        usuario: Usuario
    ):
        if usuario.perfil == "Gestão":
            return PrazoRepository.listar_por_responsavel(
                db, id_responsavel
            )

        # O aluno só pode consultar os próprios prazos.
        if usuario.perfil == "Aluno":
            if id_responsavel != usuario.id_usuario:
                raise PermissionError(
                    "Você só pode consultar seus próprios prazos."
                )

        elif usuario.perfil != "Professor":
            raise PermissionError(
                "Perfil sem permissão para consultar prazos."
            )

        prazos = PrazoService.listar(db, usuario)

        return [
            prazo for prazo in prazos
            if prazo.id_responsavel == id_responsavel
        ]

    # Valida a existência do caso, do responsável e da atividade vinculada.
    @staticmethod
    def _validar_relacionamentos(
        db: Session,
        id_caso: int,
        id_atividade: int | None,
        id_responsavel: int
    ):
        caso = PrazoService._buscar_caso(
            db, id_caso
        )

        if not caso:
            raise ValueError(
                "O caso jurídico informado não existe."
            )

        # Verifica se o usuário responsável existe e está ativo.
        usuario_existe = db.execute(
            text("""
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = :id_responsavel
                  AND situacao_conta = 'Ativo'
            """),
            {"id_responsavel": id_responsavel}
        ).first()

        if not usuario_existe:
            raise ValueError(
                "O usuário responsável não existe ou está inativo."
            )

        # Quando informada, a atividade deve pertencer ao caso selecionado.
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

    # Cadastra um prazo aplicando as regras de cada perfil.
    @staticmethod
    def criar(
        db: Session,
        dados,
        usuario: Usuario
    ):
        if usuario.perfil == "Aluno":

            id_aluno = PrazoService._buscar_id_aluno(
                db, usuario.id_usuario
            )

            if not id_aluno:
                raise PermissionError(
                    "Cadastro de aluno não encontrado."
                )

            # Verifica se o caso existe e pertence ao aluno autenticado.
            caso = PrazoService._buscar_caso(
                db, dados.id_caso
            )

            if not caso:
                raise ValueError(
                    "O caso jurídico informado não existe."
                )

            if caso.id_aluno_responsavel != id_aluno:
                raise PermissionError(
                    "Você só pode cadastrar prazos em casos "
                    "sob sua responsabilidade."
                )

            # O sistema define automaticamente os dados do prazo cadastrado pelo aluno.
            dados_prazo = dados.model_dump()

            dados_prazo["id_responsavel"] = usuario.id_usuario
            dados_prazo["situacao"] = "Pendente de validação"
            dados_prazo["motivo_rejeicao"] = None
            dados_prazo["data_conclusao"] = None

            tipo_ocorrencia = "Cadastro de prazo"
            descricao_historico = (
                f"O aluno cadastrou o prazo '{dados.descricao}'. "
                "O prazo aguarda validação do Professor ou da Gestão."
            )

        elif usuario.perfil == "Gestão":

            dados_prazo = dados.model_dump()

            # Exige justificativa quando a Gestão cadastra um prazo rejeitado.
            if dados_prazo["situacao"] == "Rejeitado":
                if not dados_prazo.get("motivo_rejeicao"):
                    raise ValueError(
                        "Informe o motivo da rejeição do prazo."
                    )

            else:
                dados_prazo["motivo_rejeicao"] = None

            tipo_ocorrencia = "Cadastro de prazo"
            descricao_historico = (
                f"A Gestão cadastrou o prazo '{dados.descricao}'."
            )

        else:
            raise PermissionError(
                "Somente Aluno ou Gestão pode cadastrar prazos."
            )

        # Confere se os relacionamentos informados são válidos.
        PrazoService._validar_relacionamentos(
            db,
            dados_prazo["id_caso"],
            dados_prazo["id_atividade"],
            dados_prazo["id_responsavel"]
        )

        # Registra a data de conclusão quando o prazo já é cadastrado como concluído.
        if dados_prazo["situacao"] == "Concluído":
            dados_prazo["data_conclusao"] = datetime.now()

        try:
            prazo = Prazo(**dados_prazo)

            db.add(prazo)
            db.flush()

            # Registra o cadastro do prazo no histórico do caso.
            PrazoService._registrar_historico(
                db,
                prazo.id_caso,
                usuario,
                tipo_ocorrencia,
                descricao_historico,
                prazo.id_prazo
            )

            db.commit()
            db.refresh(prazo)

            return prazo

        # Trata erros de integridade durante o cadastro.
        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível cadastrar o prazo. "
                "Verifique os dados informados."
            )

        # Desfaz a transação caso ocorra qualquer outro erro.
        except Exception:
            db.rollback()
            raise

    # Atualiza um prazo e controla as decisões de aprovação ou rejeição.
    @staticmethod
    def atualizar(
        db: Session,
        id_prazo: int,
        dados,
        usuario: Usuario
    ):
        # O aluno não pode validar nem atualizar prazos.
        if usuario.perfil == "Aluno":
            raise PermissionError(
                "O Aluno não possui permissão para validar "
                "ou atualizar prazos."
            )

        if usuario.perfil not in ["Gestão", "Professor"]:
            raise PermissionError(
                "Perfil sem permissão para atualizar prazos."
            )

        prazo = PrazoService.buscar_por_id(
            db, id_prazo, usuario
        )

        dados_atualizacao = dados.model_dump(
            exclude_unset=True
        )

        # Professor só pode aprovar ou rejeitar prazos dos casos sob sua orientação.
        if usuario.perfil == "Professor":

            campos_permitidos = {
                "situacao",
                "motivo_rejeicao"
            }

            if not dados_atualizacao:
                raise ValueError(
                    "Informe a decisão sobre o prazo."
                )

            # Impede que o professor altere campos além da decisão e justificativa.
            if not set(dados_atualizacao).issubset(
                campos_permitidos
            ):
                raise PermissionError(
                    "O Professor só pode aprovar ou rejeitar "
                    "prazos."
                )

            if prazo.situacao != "Pendente de validação":
                raise ValueError(
                    "Somente prazos pendentes de validação "
                    "podem ser analisados."
                )

            # As únicas decisões permitidas ao professor são aprovar ou rejeitar.
            if dados_atualizacao.get("situacao") not in [
                "Pendente",
                "Rejeitado"
            ]:
                raise ValueError(
                    "O Professor só pode aprovar ou rejeitar "
                    "o prazo."
                )

        nova_situacao = dados_atualizacao.get(
            "situacao",
            prazo.situacao
        )

        tipo_ocorrencia = None
        descricao_historico = None

        # Registra a aprovação do prazo.
        if (
            prazo.situacao == "Pendente de validação"
            and nova_situacao == "Pendente"
        ):
            dados_atualizacao["motivo_rejeicao"] = None

            tipo_ocorrencia = "Prazo aprovado"
            descricao_historico = (
                f"O prazo '{prazo.descricao}' foi aprovado "
                f"por {usuario.perfil}."
            )

        # Registra a rejeição e exige uma justificativa.
        elif nova_situacao == "Rejeitado":

            if prazo.situacao != "Pendente de validação":
                raise ValueError(
                    "Somente prazos pendentes de validação "
                    "podem ser rejeitados."
                )

            motivo = dados_atualizacao.get(
                "motivo_rejeicao"
            )

            if not motivo or not motivo.strip():
                raise ValueError(
                    "Informe o motivo da rejeição do prazo."
                )

            dados_atualizacao["motivo_rejeicao"] = motivo.strip()

            tipo_ocorrencia = "Prazo rejeitado"
            descricao_historico = (
                f"O prazo '{prazo.descricao}' foi rejeitado "
                f"por {usuario.perfil}. "
                f"Motivo: {motivo.strip()}"
            )

        # Impede informar justificativa de rejeição em outros estados.
        elif (
            "motivo_rejeicao" in dados_atualizacao
            and nova_situacao != "Rejeitado"
        ):
            raise ValueError(
                "O motivo da rejeição só pode ser informado "
                "para prazos rejeitados."
            )

        # Garante que toda atualização feita pelo professor seja uma decisão válida.
        if usuario.perfil == "Professor":
            if tipo_ocorrencia is None:
                raise ValueError(
                    "Não foi possível identificar uma decisão válida."
                )

        id_caso = dados_atualizacao.get(
            "id_caso",
            prazo.id_caso
        )

        id_atividade = dados_atualizacao.get(
            "id_atividade",
            prazo.id_atividade
        )

        id_responsavel = dados_atualizacao.get(
            "id_responsavel",
            prazo.id_responsavel
        )

        # Valida os relacionamentos considerando os dados atuais e os novos valores.
        PrazoService._validar_relacionamentos(
            db,
            id_caso,
            id_atividade,
            id_responsavel
        )

        # Define a data de conclusão ao concluir o prazo.
        if nova_situacao == "Concluído":
            if prazo.situacao != "Concluído":
                dados_atualizacao["data_conclusao"] = datetime.now()

        # Limpa a data de conclusão quando o prazo deixa de estar concluído.
        elif "situacao" in dados_atualizacao:
            dados_atualizacao["data_conclusao"] = None

        try:
            for campo, valor in dados_atualizacao.items():
                setattr(prazo, campo, valor)

            # Registra no histórico as decisões de aprovação ou rejeição.
            if tipo_ocorrencia:
                PrazoService._registrar_historico(
                    db,
                    prazo.id_caso,
                    usuario,
                    tipo_ocorrencia,
                    descricao_historico,
                    prazo.id_prazo
                )

            db.commit()
            db.refresh(prazo)

            return prazo

        # Trata erros de integridade durante a atualização.
        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível atualizar o prazo."
            )

        # Desfaz a transação caso ocorra qualquer outro erro.
        except Exception:
            db.rollback()
            raise
