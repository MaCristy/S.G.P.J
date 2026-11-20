
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.assistido import AssistidoRepository
from app.schemas.assistido import AssistidoCreate, AssistidoUpdate

from app.repositories.aluno import AlunoRepository
from app.repositories.professor import ProfessorRepository


class AssistidoService:
    """Contém as regras de negócio dos assistidos."""

    # Lista todos os assistidos cadastrados.
    @staticmethod
    def listar(db: Session):
        return AssistidoRepository.listar(db)

    # Lista os assistidos vinculados aos casos do aluno.
    @staticmethod
    def listar_por_aluno(db: Session, id_usuario: int):
        aluno = AlunoRepository.buscar_por_usuario(
            db, id_usuario
        )

        if not aluno:
            raise LookupError("Cadastro de aluno não encontrado.")

        return AssistidoRepository.listar_por_aluno(
            db, aluno.id_aluno
        )

    # Lista os assistidos vinculados aos casos supervisionados pelo professor.
    @staticmethod
    def listar_por_professor(db: Session, id_usuario: int):
        professor = ProfessorRepository.buscar_por_usuario(
            db, id_usuario
        )

        if not professor:
            raise LookupError("Cadastro de professor não encontrado.")

        # Impede a consulta caso o cadastro do professor esteja inativo.
        if professor.situacao != "Ativo":
            raise PermissionError(
                "O cadastro do professor não está ativo."
            )

        return AssistidoRepository.listar_por_professor(
            db, professor.id_professor
        )

    # Busca um assistido pelo identificador do cadastro.
    @staticmethod
    def buscar_por_id(db: Session, id_assistido: int):
        assistido = AssistidoRepository.buscar_por_id(
            db, id_assistido
        )

        if not assistido:
            raise LookupError("Assistido não encontrado.")

        return assistido

    # Busca um assistido somente quando está vinculado a um caso do aluno.
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
                "Assistido não encontrado ou não vinculado aos seus casos."
            )

        return assistido

    # Busca um assistido somente quando está vinculado a um caso supervisionado pelo professor.
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

        # Impede o acesso caso o cadastro do professor esteja inativo.
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

    # Cadastra um assistido após verificar a existência de identificador duplicado.
    @staticmethod
    def criar(db: Session, dados: AssistidoCreate):
        existente = AssistidoRepository.buscar_por_identificador(
            db,
            dados.identificador_cadastral
        )

        if existente:
            raise ValueError(
                "Já existe um assistido com esse identificador cadastral."
            )

        # Persiste o cadastro e confirma a transação.
        try:
            assistido = AssistidoRepository.criar(db, dados)
            db.commit()
            db.refresh(assistido)

            return assistido

        # Desfaz a transação caso ocorra uma violação de integridade.
        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível cadastrar. Verifique se o identificador cadastral já existe."
            )

        # Desfaz a transação diante de qualquer outro erro inesperado.
        except Exception:
            db.rollback()
            raise

    # Atualiza os dados de um assistido, verificando campos obrigatórios e duplicidades.
    @staticmethod
    def atualizar(
        db: Session,
        id_assistido: int,
        dados: AssistidoUpdate
    ):
        assistido = AssistidoRepository.buscar_por_id(
            db, id_assistido
        )

        if not assistido:
            raise LookupError("Assistido não encontrado.")

        # Obtém somente os campos enviados na solicitação de atualização.
        dados_atualizados = dados.model_dump(exclude_unset=True)

        # Impede que campos obrigatórios sejam atualizados com valor nulo.
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

        # Verifica se o novo identificador já pertence a outro assistido.
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

        # Persiste as alterações e atualiza os dados do objeto.
        try:
            assistido = AssistidoRepository.atualizar(
                db,
                assistido,
                dados
            )

            db.commit()
            db.refresh(assistido)

            return assistido

        # Desfaz a transação caso ocorra uma violação de integridade.
        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível atualizar. Verifique os dados informados."
            )

        # Desfaz a transação diante de qualquer outro erro inesperado.
        except Exception:
            db.rollback()
            raise
