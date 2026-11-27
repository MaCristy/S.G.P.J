
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.assistido import AssistidoRepository
from app.schemas.assistido import AssistidoCreate, AssistidoUpdate

from app.repositories.aluno import AlunoRepository
from app.repositories.professor import ProfessorRepository


class AssistidoService:
    """Contém as regras de negócio dos assistidos."""

    @staticmethod
    def listar(db: Session):
        return AssistidoRepository.listar(db)

    @staticmethod
    def listar_por_aluno(db: Session, id_usuario: int):
        aluno = AlunoRepository.buscar_por_usuario(db, id_usuario)

        if not aluno:
            raise LookupError("Cadastro de aluno não encontrado.")

        return AssistidoRepository.listar_por_aluno(
            db, aluno.id_aluno
        )

    @staticmethod
    def listar_por_professor(db: Session, id_usuario: int):
        professor = ProfessorRepository.buscar_por_usuario(
            db, id_usuario
        )

        if not professor:
            raise LookupError("Cadastro de professor não encontrado.")

        if professor.situacao != "Ativo":
            raise PermissionError(
                "O cadastro do professor não está ativo."
            )

        return AssistidoRepository.listar_por_professor(
            db, professor.id_professor
        )

    @staticmethod
    def buscar_por_id(db: Session, id_assistido: int):
        assistido = AssistidoRepository.buscar_por_id(
            db, id_assistido
        )

        if not assistido:
            raise LookupError("Assistido não encontrado.")

        return assistido

    @staticmethod
    def buscar_por_id_e_aluno(
        db: Session,
        id_assistido: int,
        id_usuario: int
    ):
        aluno = AlunoRepository.buscar_por_usuario(
            db, id_usuario
        )

        if not aluno:
            raise LookupError("Cadastro de aluno não encontrado.")

        assistido = AssistidoRepository.buscar_por_id_e_aluno(
            db,
            id_assistido,
            aluno.id_aluno
        )

        if not assistido:
            raise LookupError(
                "Assistido não encontrado ou sem vínculo com você."
            )

        return assistido

    @staticmethod
    def buscar_por_id_e_professor(
        db: Session,
        id_assistido: int,
        id_usuario: int
    ):
        professor = ProfessorRepository.buscar_por_usuario(
            db, id_usuario
        )

        if not professor:
            raise LookupError("Cadastro de professor não encontrado.")

        if professor.situacao != "Ativo":
            raise PermissionError(
                "O cadastro do professor não está ativo."
            )

        assistido = AssistidoRepository.buscar_por_id_e_professor(
            db,
            id_assistido,
            professor.id_professor
        )

        if not assistido:
            raise LookupError(
                "Assistido não encontrado ou não vinculado aos seus casos."
            )

        return assistido

    # Cadastra o assistido e identifica o aluno responsável, quando aplicável.
    @staticmethod
    def criar(
        db: Session,
        dados: AssistidoCreate,
        usuario_atual
    ):
        id_aluno_cadastro = None

        if usuario_atual.perfil == "Aluno":
            aluno = AlunoRepository.buscar_por_usuario(
                db, usuario_atual.id_usuario
            )

            if not aluno:
                raise LookupError("Cadastro de aluno não encontrado.")

            id_aluno_cadastro = aluno.id_aluno

        elif usuario_atual.perfil != "Gestão":
            raise PermissionError(
                "Você não possui permissão para cadastrar assistidos."
            )

        existente = AssistidoRepository.buscar_por_identificador(
            db,
            dados.identificador_cadastral
        )

        if existente:
            raise ValueError(
                "Já existe um assistido com esse identificador cadastral."
            )

        try:
            assistido = AssistidoRepository.criar(
                db,
                dados,
                id_aluno_cadastro=id_aluno_cadastro
            )

            db.commit()
            db.refresh(assistido)

            return assistido

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível cadastrar. Verifique se o identificador cadastral já existe."
            )

        except Exception:
            db.rollback()
            raise

    # Atualiza os dados conforme as permissões do perfil.
    @staticmethod
    def atualizar(
        db: Session,
        id_assistido: int,
        dados: AssistidoUpdate,
        usuario_atual
    ):
        if usuario_atual.perfil == "Gestão":
            assistido = AssistidoRepository.buscar_por_id(
                db, id_assistido
            )

        elif usuario_atual.perfil == "Aluno":
            aluno = AlunoRepository.buscar_por_usuario(
                db, usuario_atual.id_usuario
            )

            if not aluno:
                raise LookupError("Cadastro de aluno não encontrado.")

            assistido = AssistidoRepository.buscar_por_id_e_aluno(
                db,
                id_assistido,
                aluno.id_aluno
            )

            if not assistido:
                raise PermissionError(
                    "Você só pode atualizar assistidos cadastrados por você ou vinculados aos seus casos."
                )

        else:
            raise PermissionError(
                "Você não possui permissão para atualizar assistidos."
            )

        if not assistido:
            raise LookupError("Assistido não encontrado.")

        dados_atualizados = dados.model_dump(exclude_unset=True)

        campos_obrigatorios = [
            "nome_completo",
            "identificador_cadastral",
            "contato",
            "situacao"
        ]

        for campo in campos_obrigatorios:
            if campo in dados_atualizados and dados_atualizados[campo] is None:
                raise ValueError(
                    f"O campo '{campo}' não pode ficar vazio."
                )

        novo_identificador = dados_atualizados.get(
            "identificador_cadastral"
        )

        if novo_identificador:
            existente = AssistidoRepository.buscar_por_identificador(
                db,
                novo_identificador
            )

            if (
                existente
                and existente.id_assistido != id_assistido
            ):
                raise ValueError(
                    "Esse identificador cadastral já pertence a outro assistido."
                )

        try:
            assistido = AssistidoRepository.atualizar(
                db,
                assistido,
                dados
            )

            db.commit()
            db.refresh(assistido)

            return assistido

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível atualizar. Verifique os dados informados."
            )

        except Exception:
            db.rollback()
            raise
