
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.usuario import Usuario
from app.repositories.aluno import AlunoRepository
from app.repositories.professor import ProfessorRepository
from app.schemas.aluno import AlunoCreate, AlunoUpdate


class AlunoService:

    # Verifica se o usuário existe e possui o perfil de Aluno.
    @staticmethod
    def validar_usuario_aluno(db: Session, id_usuario: int):
        usuario = (
            db.query(Usuario)
            .filter(Usuario.id_usuario == id_usuario)
            .first()
        )

        if not usuario:
            raise LookupError("Usuário informado não encontrado.")

        if usuario.perfil != "Aluno":
            raise ValueError(
                "O usuário informado não possui perfil de Aluno."
            )

        return usuario

    # Lista todos os alunos cadastrados no sistema.
    @staticmethod
    def listar(db: Session):
        return AlunoRepository.listar(db)

    # Lista os alunos vinculados aos casos supervisionados pelo professor.
    @staticmethod
    def listar_por_professor(db: Session, id_usuario: int):
        # Busca o cadastro de professor associado ao usuário.
        professor = ProfessorRepository.buscar_por_usuario(
            db, id_usuario
        )

        if not professor:
            raise LookupError(
                "Cadastro de professor não encontrado."
            )

        # Impede a consulta caso o cadastro do professor esteja inativo.
        if professor.situacao != "Ativo":
            raise PermissionError(
                "O cadastro do professor não está ativo."
            )

        return AlunoRepository.listar_por_professor(
            db, professor.id_professor
        )

    # Busca o cadastro de aluno pelo identificador do usuário.
    @staticmethod
    def buscar_por_usuario(db: Session, id_usuario: int):
        aluno = AlunoRepository.buscar_por_usuario(
            db, id_usuario
        )

        if not aluno:
            raise LookupError("Cadastro de aluno não encontrado.")

        return aluno

    # Busca um aluno pelo identificador do cadastro.
    @staticmethod
    def buscar_por_id(db: Session, id_aluno: int):
        aluno = AlunoRepository.buscar_por_id(db, id_aluno)

        if not aluno:
            raise LookupError("Aluno não encontrado.")

        return aluno

    # Cadastra um aluno após validar os dados e os vínculos informados.
    @staticmethod
    def criar(db: Session, dados: AlunoCreate):

        # Verifica a existência e o perfil do usuário informado.
        AlunoService.validar_usuario_aluno(
            db, dados.id_usuario
        )

        # Impede que um mesmo usuário possua mais de um cadastro de aluno.
        aluno_usuario = AlunoRepository.buscar_por_usuario(
            db, dados.id_usuario
        )

        if aluno_usuario:
            raise ValueError(
                "Esse usuário já possui um cadastro como aluno."
            )

        # Verifica se a matrícula já está vinculada a outro aluno.
        aluno_matricula = AlunoRepository.buscar_por_matricula(
            db, dados.matricula
        )

        if aluno_matricula:
            raise ValueError(
                "Já existe um aluno cadastrado com essa matrícula."
            )

        # Persiste o cadastro e confirma a transação no banco.
        try:
            aluno = AlunoRepository.criar(db, dados)

            db.commit()
            db.refresh(aluno)

            return aluno

        # Desfaz a transação caso ocorra uma violação de integridade.
        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível cadastrar o aluno. "
                "Verifique os dados e os vínculos informados."
            )

        # Desfaz a transação diante de qualquer outro erro inesperado.
        except Exception:
            db.rollback()
            raise

    # Atualiza os dados de um aluno, verificando possíveis duplicidades.
    @staticmethod
    def atualizar(db: Session, id_aluno: int, dados: AlunoUpdate):

        # Verifica se o aluno que será atualizado está cadastrado.
        aluno = AlunoRepository.buscar_por_id(db, id_aluno)

        if not aluno:
            raise LookupError("Aluno não encontrado.")

        # Obtém somente os campos enviados na solicitação de atualização.
        dados_atualizacao = dados.model_dump(
            exclude_unset=True,
            exclude_none=True
        )

        # Valida o novo usuário caso o vínculo seja alterado.
        if "id_usuario" in dados_atualizacao:

            AlunoService.validar_usuario_aluno(
                db, dados_atualizacao["id_usuario"]
            )

            # Impede que o mesmo usuário seja vinculado a outro aluno.
            outro_aluno = AlunoRepository.buscar_por_usuario(
                db, dados_atualizacao["id_usuario"]
            )

            if outro_aluno and outro_aluno.id_aluno != id_aluno:
                raise ValueError(
                    "Esse usuário já possui cadastro como aluno."
                )

        # Verifica se a nova matrícula já pertence a outro aluno.
        if "matricula" in dados_atualizacao:

            outra_matricula = AlunoRepository.buscar_por_matricula(
                db, dados_atualizacao["matricula"]
            )

            if outra_matricula and outra_matricula.id_aluno != id_aluno:
                raise ValueError(
                    "Já existe um aluno cadastrado com essa matrícula."
                )

        # Persiste as alterações e atualiza os dados do objeto.
        try:
            aluno = AlunoRepository.atualizar(
                db, aluno, dados_atualizacao
            )

            db.commit()
            db.refresh(aluno)

            return aluno

        # Desfaz a transação caso ocorra uma violação de integridade.
        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível atualizar o cadastro do aluno."
            )

        # Desfaz a transação diante de qualquer outro erro inesperado.
        except Exception:
            db.rollback()
            raise
