
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.caso_juridico import CasoJuridicoRepository
from app.repositories.assistido import AssistidoRepository
from app.repositories.aluno import AlunoRepository
from app.repositories.professor import ProfessorRepository

from app.schemas.caso_juridico import CasoJuridicoCreate
from app.models.historico_caso import HistoricoCaso


class CasoJuridicoService:

    # Retorna todos os casos jurídicos cadastrados.
    @staticmethod
    def listar(db: Session):
        return CasoJuridicoRepository.listar(db)

    # Busca um caso pelo identificador.
    @staticmethod
    def buscar_por_id(db: Session, id_caso: int):
        caso = CasoJuridicoRepository.buscar_por_id(db, id_caso)

        if not caso:
            raise LookupError("Caso jurídico não encontrado.")

        return caso

    # Lista os casos vinculados a um assistido existente.
    @staticmethod
    def listar_por_assistido(db: Session, id_assistido: int):
        assistido = AssistidoRepository.buscar_por_id(db, id_assistido)

        if not assistido:
            raise LookupError("Assistido não encontrado.")

        return CasoJuridicoRepository.listar_por_assistido(
            db, id_assistido
        )

    # Lista os casos sob responsabilidade do aluno autenticado.
    @staticmethod
    def listar_por_aluno(db: Session, id_usuario: int):
        aluno = AlunoRepository.buscar_por_usuario(db, id_usuario)

        if not aluno:
            raise LookupError("Cadastro de aluno não encontrado.")

        return CasoJuridicoRepository.listar_por_aluno(
            db, aluno.id_aluno
        )

    # Lista os casos sob orientação do professor autenticado.
    @staticmethod
    def listar_por_professor(db: Session, id_usuario: int):
        professor = ProfessorRepository.buscar_por_usuario(
            db, id_usuario
        )

        if not professor:
            raise LookupError(
                "Cadastro de professor não encontrado ou inativo."
            )

        return CasoJuridicoRepository.listar_por_professor(
            db, professor.id_professor
        )

    # Cadastra um caso jurídico aplicando as regras de negócio.
    @staticmethod
    def criar(
        db: Session,
        dados: CasoJuridicoCreate,
        usuario
    ):
        # Verifica se o assistido informado existe.
        assistido = AssistidoRepository.buscar_por_id(
            db, dados.id_assistido
        )

        if not assistido:
            raise LookupError("Assistido não encontrado.")

        # Impede a criação de casos para assistidos inativos.
        if assistido.situacao != "Ativo":
            raise ValueError(
                "Não é possível cadastrar um caso para um assistido inativo."
            )

        # Impede a utilização de um código interno já cadastrado.
        codigo_existente = CasoJuridicoRepository.buscar_por_codigo(
            db, dados.codigo_interno
        )

        if codigo_existente:
            raise ValueError(
                "Já existe um caso com esse código interno."
            )

        dados_caso = dados.model_dump()

        # Aplica as regras específicas para o cadastro realizado pelo aluno.
        if usuario.perfil == "Aluno":
            aluno = AlunoRepository.buscar_por_usuario(
                db, usuario.id_usuario
            )

            if not aluno:
                raise LookupError("Cadastro de aluno não encontrado.")

            # O aluno passa a ser o responsável pelo caso.
            dados_caso["id_aluno_responsavel"] = aluno.id_aluno

            # Mantém o professor orientador escolhido pelo aluno.
            # A validação do professor será realizada abaixo.

            # Todo caso aberto pelo aluno começa em triagem.
            dados_caso["situacao"] = "Em triagem"
            dados_caso["data_encerramento"] = None

        elif usuario.perfil != "Gestão":
            raise PermissionError(
                "Somente Aluno ou Gestão podem cadastrar casos jurídicos."
            )

        # Valida o aluno responsável informado, quando houver.
        id_aluno = dados_caso["id_aluno_responsavel"]

        if id_aluno is not None:
            aluno_responsavel = AlunoRepository.buscar_por_id(
                db, id_aluno
            )

            if not aluno_responsavel:
                raise LookupError("Aluno responsável não encontrado.")

        # Valida o professor orientador informado, quando houver.
        id_professor = dados_caso["id_professor_orientador"]

        if id_professor is not None:
            professor_orientador = ProfessorRepository.buscar_por_id(
                db, id_professor
            )

        if not professor_orientador:
            raise LookupError("Professor orientador não encontrado.")

        if professor_orientador.situacao != "Ativo":
            raise ValueError(
                "O professor orientador selecionado não está ativo."
            )

        try:
            # Cria o caso com os dados já validados.
            caso = CasoJuridicoRepository.criar(
                db,
                CasoJuridicoCreate(**dados_caso)
            )

            db.flush()
            db.refresh(caso)

            # Registra o cadastro no histórico do caso.
            db.add(
                HistoricoCaso(
                    id_caso=caso.id_caso,
                    id_usuario_responsavel=usuario.id_usuario,
                    tipo_ocorrencia=(
                        "Cadastro de caso em triagem"
                        if usuario.perfil == "Aluno"
                        else "Cadastro de caso"
                    ),
                    descricao=(
                        "Caso cadastrado pelo aluno e encaminhado para validação."
                        if usuario.perfil == "Aluno"
                        else "Caso cadastrado pela Gestão."
                    ),
                    referencia_registro_afetado=f"caso:{caso.id_caso}"
                )
            )

            # Confirma o cadastro e o registro do histórico.
            db.commit()
            db.refresh(caso)

            return caso

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível cadastrar o caso jurídico. "
                "Verifique os dados e os relacionamentos informados."
            )

        except Exception:
            db.rollback()
            raise
