
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.usuario import Usuario
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.solicitacao_cadastro import SolicitacaoCadastro

from app.repositories.usuario import UsuarioRepository
from app.repositories.aluno import AlunoRepository
from app.repositories.professor import ProfessorRepository
from app.repositories.solicitacao_cadastro import (
    SolicitacaoCadastroRepository
)

from app.schemas.solicitacao_cadastro import (
    SolicitacaoCadastroCreate,
    SolicitacaoCadastroAprovacao,
    SolicitacaoCadastroRejeicao
)

from app.core.security import gerar_hash_senha


class SolicitacaoCadastroService:

    # Verifica se o usuário informado é um gestor ativo.
    @staticmethod
    def validar_gestor(db: Session, id_gestor: int):

        gestor = UsuarioRepository.buscar_por_id(
            db, id_gestor
        )

        if not gestor:
            raise LookupError("Gestor não encontrado.")

        if gestor.perfil != "Gestão":
            raise PermissionError(
                "Somente usuários da Gestão podem analisar solicitações."
            )

        if gestor.situacao_conta != "Ativo":
            raise PermissionError(
                "A conta do gestor não está ativa."
            )

        return gestor

    # Lista as solicitações, permitindo filtrar pelo status.
    @staticmethod
    def listar(db: Session, status_solicitacao: str | None = None):

        return SolicitacaoCadastroRepository.listar(
            db, status_solicitacao
        )

    # Busca uma solicitação pelo identificador.
    @staticmethod
    def buscar_por_id(db: Session, id_solicitacao: int):

        solicitacao = SolicitacaoCadastroRepository.buscar_por_id(
            db, id_solicitacao
        )

        if not solicitacao:
            raise LookupError("Solicitação de cadastro não encontrada.")

        return solicitacao

    # Verifica se a matrícula já está vinculada a outro aluno.
    @staticmethod
    def validar_matricula(
        db: Session,
        matricula: str,
        id_solicitacao: int | None = None
    ):

        aluno = AlunoRepository.buscar_por_matricula(
            db, matricula
        )

        if aluno:
            raise ValueError(
                "Já existe um aluno cadastrado com essa matrícula."
            )

        solicitacao = (
            SolicitacaoCadastroRepository
            .buscar_pendente_por_matricula(db, matricula)
        )

        # Na aprovação, ignora a própria solicitação que está sendo analisada.
        if solicitacao and solicitacao.id_solicitacao != id_solicitacao:
            raise ValueError(
                "Já existe uma solicitação pendente utilizando essa matrícula."
            )

    # Verifica se a identificação funcional já está vinculada a um professor.
    @staticmethod
    def validar_identificacao_funcional(
        db: Session,
        identificacao_funcional: str,
        id_solicitacao: int | None = None
    ):

        professor = ProfessorRepository.buscar_por_identificacao(
            db, identificacao_funcional
        )

        if professor:
            raise ValueError(
                "Já existe um professor cadastrado com essa identificação funcional."
            )

        solicitacao = (
            SolicitacaoCadastroRepository
            .buscar_pendente_por_identificacao_funcional(
                db, identificacao_funcional
            )
        )

        # Na aprovação, ignora a própria solicitação que está sendo analisada.
        if solicitacao and solicitacao.id_solicitacao != id_solicitacao:
            raise ValueError(
                "Já existe uma solicitação pendente utilizando essa identificação funcional."
            )

    # Recebe uma solicitação pública e cria ou reutiliza a conta do usuário.
    @staticmethod
    def criar(db: Session, dados: SolicitacaoCadastroCreate):

        usuario = None

        try:
            # Impede que o mesmo usuário tenha duas solicitações pendentes.
            usuario_existente = UsuarioRepository.buscar_por_email(
                db, dados.email_institucional
            )

            if usuario_existente:

                # Identifica primeiro uma solicitação que ainda está em análise.
                # Assim, a API informa o motivo correto em vez de tratar o caso
                # apenas como uma conta já cadastrada.
                solicitacao_pendente = (
                    SolicitacaoCadastroRepository.buscar_pendente_por_usuario(
                        db, usuario_existente.id_usuario
                    )
                )

                if solicitacao_pendente:
                    raise ValueError(
                        "Já existe uma solicitação de cadastro pendente "
                        "para esse usuário."
                    )

                # Somente contas rejeitadas podem solicitar novamente.
                if usuario_existente.situacao_conta != "Rejeitado":
                    raise ValueError(
                        "Já existe uma conta cadastrada com esse e-mail."
                    )

                # Recupera a última solicitação para verificar o histórico.
                ultima_solicitacao = (
                    SolicitacaoCadastroRepository
                    .buscar_ultima_por_usuario(
                        db, usuario_existente.id_usuario
                    )
                )

                if (
                    not ultima_solicitacao
                    or ultima_solicitacao.status_solicitacao != "Rejeitada"
                ):
                    raise ValueError(
                        "Não foi possível identificar uma solicitação "
                        "rejeitada que permita um novo pedido."
                    )

                # Impede a troca do perfil na reutilização da conta.
                if (
                    ultima_solicitacao.perfil_solicitado
                    != dados.perfil_solicitado
                ):
                    raise ValueError(
                        "O novo pedido deve utilizar o mesmo perfil "
                        "da solicitação rejeitada."
                    )

                # Exige a mesma matrícula para uma nova solicitação de aluno.
                if dados.perfil_solicitado == "Aluno":
                    if ultima_solicitacao.matricula != dados.matricula:
                        raise ValueError(
                            "A nova solicitação deve utilizar a mesma "
                            "matrícula da solicitação rejeitada."
                        )

                # Exige a mesma identificação funcional para professor.
                if dados.perfil_solicitado == "Professor":
                    if (
                        ultima_solicitacao.identificacao_funcional
                        != dados.identificacao_funcional
                    ):
                        raise ValueError(
                            "A nova solicitação deve utilizar a mesma "
                            "identificação funcional da solicitação rejeitada."
                        )

                usuario = usuario_existente

                # Atualiza os dados da conta e libera um novo pedido.
                usuario.nome = dados.nome
                usuario.senha_armazenada = gerar_hash_senha(
                    dados.senha
                )
                usuario.situacao_conta = "Pendente"

            else:

                # Verifica se o identificador já pertence a um cadastro definitivo.
                if dados.perfil_solicitado == "Aluno":
                    SolicitacaoCadastroService.validar_matricula(
                        db, dados.matricula
                    )

                else:
                    SolicitacaoCadastroService.validar_identificacao_funcional(
                        db, dados.identificacao_funcional
                    )

                # Cria a conta pública inicialmente bloqueada.
                usuario = Usuario(
                    nome=dados.nome,
                    email_institucional=dados.email_institucional,
                    senha_armazenada=gerar_hash_senha(dados.senha),
                    perfil=dados.perfil_solicitado,
                    situacao_conta="Pendente"
                )

                db.add(usuario)
                db.flush()

            # Verifica novamente se o identificador está disponível.
            # Essa verificação também protege o fluxo de reenvio.
            if dados.perfil_solicitado == "Aluno":

                SolicitacaoCadastroService.validar_matricula(
                    db, dados.matricula
                )

            else:

                SolicitacaoCadastroService.validar_identificacao_funcional(
                    db, dados.identificacao_funcional
                )

            # Prepara os dados da nova solicitação.
            dados_solicitacao = {
                "id_usuario": usuario.id_usuario,
                "perfil_solicitado": dados.perfil_solicitado,
                "matricula": dados.matricula,
                "curso": dados.curso,
                "periodo": dados.periodo,
                "identificacao_funcional": dados.identificacao_funcional,
                "area_vinculo": dados.area_vinculo,
                "status_solicitacao": "Pendente"
            }

            # Cria a solicitação sem substituir o histórico anterior.
            solicitacao = SolicitacaoCadastroRepository.criar(
                db, dados_solicitacao
            )

            db.commit()
            db.refresh(solicitacao)

            return solicitacao

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível registrar a solicitação. "
                "Verifique se o e-mail ou identificador já está em uso."
            )

        except Exception:
            db.rollback()
            raise

    # Aprova uma solicitação e cria o cadastro definitivo correspondente.
    @staticmethod
    def aprovar(
        db: Session,
        id_solicitacao: int,
        id_gestor: int,
        dados: SolicitacaoCadastroAprovacao
    ):

        try:
            # Confirma que o responsável pela análise é um gestor ativo.
            SolicitacaoCadastroService.validar_gestor(
                db, id_gestor
            )

            solicitacao = SolicitacaoCadastroService.buscar_por_id(
                db, id_solicitacao
            )

            if solicitacao.status_solicitacao != "Pendente":
                raise ValueError(
                    "Somente solicitações pendentes podem ser aprovadas."
                )

            usuario = UsuarioRepository.buscar_por_id(
                db, solicitacao.id_usuario
            )

            if not usuario:
                raise LookupError(
                    "Usuário associado à solicitação não encontrado."
                )

            # Confere se o usuário ainda possui uma conta pendente.
            if usuario.situacao_conta != "Pendente":
                raise ValueError(
                    "A conta do usuário não está pendente de aprovação."
                )

            # Cria o cadastro acadêmico definitivo do aluno.
            if solicitacao.perfil_solicitado == "Aluno":

                if (
                    dados.situacao_academica is None
                    or not dados.situacao_academica.strip()
                    or dados.data_vinculo is None
                ):
                    raise ValueError(
                        "Informe a situação acadêmica e a data de vínculo "
                        "para aprovar o cadastro do aluno."
                    )

                SolicitacaoCadastroService.validar_matricula(
                    db,
                    solicitacao.matricula,
                    solicitacao.id_solicitacao
                )

                aluno = Aluno(
                    id_usuario=usuario.id_usuario,
                    matricula=solicitacao.matricula,
                    curso=solicitacao.curso,
                    periodo=solicitacao.periodo,
                    situacao_academica=dados.situacao_academica.strip(),
                    data_vinculo=dados.data_vinculo
                )

                db.add(aluno)

                solicitacao.situacao_academica = (
                    dados.situacao_academica.strip()
                )
                solicitacao.data_vinculo = dados.data_vinculo

            # Cria o cadastro definitivo do professor.
            elif solicitacao.perfil_solicitado == "Professor":

                SolicitacaoCadastroService.validar_identificacao_funcional(
                    db,
                    solicitacao.identificacao_funcional,
                    solicitacao.id_solicitacao
                )

                professor = Professor(
                    id_usuario=usuario.id_usuario,
                    identificacao_funcional=(
                        solicitacao.identificacao_funcional
                    ),
                    area_vinculo=solicitacao.area_vinculo,
                    situacao="Ativo"
                )

                db.add(professor)

            # Ativa a conta somente após criar o cadastro definitivo.
            usuario.situacao_conta = "Ativo"

            # Registra a decisão e o gestor responsável.
            solicitacao.status_solicitacao = "Aprovada"
            solicitacao.data_analise = datetime.now()
            solicitacao.id_gestor_analise = id_gestor
            solicitacao.observacao_analise = dados.observacao_analise

            db.commit()
            db.refresh(solicitacao)

            return solicitacao

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível aprovar a solicitação. "
                "Verifique se os dados já estão cadastrados."
            )

        except Exception:
            db.rollback()
            raise

    # Rejeita uma solicitação e mantém a conta do usuário bloqueada.
    @staticmethod
    def rejeitar(
        db: Session,
        id_solicitacao: int,
        id_gestor: int,
        dados: SolicitacaoCadastroRejeicao
    ):

        try:
            # Confirma que o responsável pela análise é um gestor ativo.
            SolicitacaoCadastroService.validar_gestor(
                db, id_gestor
            )

            solicitacao = SolicitacaoCadastroService.buscar_por_id(
                db, id_solicitacao
            )

            if solicitacao.status_solicitacao != "Pendente":
                raise ValueError(
                    "Somente solicitações pendentes podem ser rejeitadas."
                )

            usuario = UsuarioRepository.buscar_por_id(
                db, solicitacao.id_usuario
            )

            if not usuario:
                raise LookupError(
                    "Usuário associado à solicitação não encontrado."
                )

            # Mantém o usuário bloqueado após a rejeição.
            usuario.situacao_conta = "Rejeitado"

            # Preserva a solicitação e registra a decisão da Gestão.
            solicitacao.status_solicitacao = "Rejeitada"
            solicitacao.data_analise = datetime.now()
            solicitacao.id_gestor_analise = id_gestor
            solicitacao.observacao_analise = dados.observacao_analise

            db.commit()
            db.refresh(solicitacao)

            return solicitacao

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível rejeitar a solicitação."
            )

        except Exception:
            db.rollback()
            raise
