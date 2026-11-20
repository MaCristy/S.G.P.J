
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.atendimento import AtendimentoRepository
from app.repositories.assistido import AssistidoRepository
from app.repositories.aluno import AlunoRepository
from app.repositories.professor import ProfessorRepository
from app.schemas.atendimento import AtendimentoCreate


class AtendimentoService:

    # Lista todos os atendimentos cadastrados.
    @staticmethod
    def listar(db: Session):
        return AtendimentoRepository.listar(db)

    # Lista os atendimentos vinculados aos casos ou registros do aluno.
    @staticmethod
    def listar_por_aluno(db: Session, id_usuario: int):
        aluno = AlunoRepository.buscar_por_usuario(
            db, id_usuario
        )

        if not aluno:
            raise LookupError("Cadastro de aluno não encontrado.")

        return AtendimentoRepository.listar_por_aluno(
            db,
            aluno.id_aluno,
            id_usuario
        )

    # Lista os atendimentos dos casos supervisionados pelo professor.
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

        return AtendimentoRepository.listar_por_professor(
            db, professor.id_professor
        )

    # Busca um atendimento pelo identificador do cadastro.
    @staticmethod
    def buscar_por_id(db: Session, id_atendimento: int):
        atendimento = AtendimentoRepository.buscar_por_id(
            db, id_atendimento
        )

        if not atendimento:
            raise LookupError("Atendimento não encontrado.")

        return atendimento

    # Busca um atendimento verificando se pertence ao aluno ou foi registrado por ele.
    @staticmethod
    def buscar_por_id_e_aluno(
        db: Session,
        id_atendimento: int,
        id_usuario: int
    ):
        aluno = AlunoRepository.buscar_por_usuario(
            db, id_usuario
        )

        if not aluno:
            raise LookupError("Cadastro de aluno não encontrado.")

        atendimento = AtendimentoRepository.buscar_por_id_e_aluno(
            db,
            id_atendimento,
            aluno.id_aluno,
            id_usuario
        )

        if not atendimento:
            raise LookupError(
                "Atendimento não encontrado ou sem vínculo autorizado."
            )

        return atendimento

    # Busca um atendimento vinculado a um caso supervisionado pelo professor.
    @staticmethod
    def buscar_por_id_e_professor(
        db: Session,
        id_atendimento: int,
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

        atendimento = AtendimentoRepository.buscar_por_id_e_professor(
            db,
            id_atendimento,
            professor.id_professor
        )

        if not atendimento:
            raise LookupError(
                "Atendimento não encontrado ou não vinculado aos seus casos."
            )

        return atendimento

    # Lista todos os atendimentos vinculados a determinado assistido.
    @staticmethod
    def listar_por_assistido(db: Session, id_assistido: int):
        assistido = AssistidoRepository.buscar_por_id(
            db, id_assistido
        )

        if not assistido:
            raise LookupError("Assistido não encontrado.")

        return AtendimentoRepository.listar_por_assistido(
            db, id_assistido
        )

    # Lista atendimentos de um assistido acessíveis ao aluno.
    @staticmethod
    def listar_por_assistido_e_aluno(
        db: Session,
        id_assistido: int,
        id_usuario: int
    ):
        assistido = AssistidoRepository.buscar_por_id(
            db, id_assistido
        )

        if not assistido:
            raise LookupError("Assistido não encontrado.")

        aluno = AlunoRepository.buscar_por_usuario(
            db, id_usuario
        )

        if not aluno:
            raise LookupError("Cadastro de aluno não encontrado.")

        return AtendimentoRepository.listar_por_assistido_e_aluno(
            db,
            id_assistido,
            aluno.id_aluno,
            id_usuario
        )

    # Lista atendimentos de um assistido vinculados aos casos do professor.
    @staticmethod
    def listar_por_assistido_e_professor(
        db: Session,
        id_assistido: int,
        id_usuario: int
    ):
        assistido = AssistidoRepository.buscar_por_id(
            db, id_assistido
        )

        if not assistido:
            raise LookupError("Assistido não encontrado.")

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

        return AtendimentoRepository.listar_por_assistido_e_professor(
            db,
            id_assistido,
            professor.id_professor
        )

    # Registra um atendimento após validar as permissões e os vínculos informados.
    @staticmethod
    def criar(
        db: Session,
        dados: AtendimentoCreate,
        id_usuario_registro: int,
        perfil_usuario: str
    ):
        # Permite o registro de atendimentos apenas para Aluno e Gestão.
        if perfil_usuario not in ["Aluno", "Gestão"]:
            raise PermissionError(
                "Seu perfil não possui permissão para registrar atendimentos."
            )

        # Verifica se o assistido informado está cadastrado.
        assistido = AssistidoRepository.buscar_por_id(
            db, dados.id_assistido
        )

        if not assistido:
            raise LookupError("Assistido não encontrado.")

        # Verifica se o usuário responsável pelo registro existe.
        usuario = db.execute(
            text("""
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = :id_usuario
            """),
            {"id_usuario": id_usuario_registro}
        ).first()

        if not usuario:
            raise LookupError("Usuário responsável não encontrado.")

        # Quando informado, verifica se o caso pertence ao assistido.
        if dados.id_caso is not None:
            caso = db.execute(
                text("""
                    SELECT id_caso, id_aluno_responsavel
                    FROM casos_juridicos
                    WHERE id_caso = :id_caso
                    AND id_assistido = :id_assistido
                """),
                {
                    "id_caso": dados.id_caso,
                    "id_assistido": dados.id_assistido
                }
            ).first()

            if not caso:
                raise ValueError(
                    "O caso informado não existe ou não pertence ao assistido."
                )

            # Garante que o aluno registre atendimentos somente nos próprios casos.
            if perfil_usuario == "Aluno":
                aluno = AlunoRepository.buscar_por_usuario(
                    db, id_usuario_registro
                )

                if not aluno:
                    raise LookupError("Cadastro de aluno não encontrado.")

                if caso.id_aluno_responsavel != aluno.id_aluno:
                    raise PermissionError(
                        "Você só pode registrar atendimentos nos seus próprios casos."
                    )

        # Persiste o atendimento e confirma a transação no banco.
        try:
            atendimento = AtendimentoRepository.criar(
                db,
                dados,
                id_usuario_registro
            )

            db.commit()
            db.refresh(atendimento)

            return atendimento

        # Desfaz a transação caso ocorra uma violação de integridade.
        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível registrar o atendimento. "
                "Verifique os relacionamentos informados."
            )

        # Desfaz a transação diante de qualquer outro erro inesperado.
        except Exception:
            db.rollback()
            raise
