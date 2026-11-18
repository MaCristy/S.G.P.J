
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.caso_juridico import CasoJuridicoRepository
from app.repositories.assistido import AssistidoRepository
from app.repositories.aluno import AlunoRepository
from app.schemas.caso_juridico import CasoJuridicoCreate
from app.models.historico_caso import HistoricoCaso
from app.repositories.professor import ProfessorRepository


class CasoJuridicoService:

    @staticmethod
    def listar(db: Session):
        return CasoJuridicoRepository.listar(db)

    @staticmethod
    def buscar_por_id(db: Session, id_caso: int):
        caso = CasoJuridicoRepository.buscar_por_id(db, id_caso)

        if not caso:
            raise LookupError("Caso jurídico não encontrado.")

        return caso

    @staticmethod
    def listar_por_assistido(db: Session, id_assistido: int):
        assistido = AssistidoRepository.buscar_por_id(db, id_assistido)

        if not assistido:
            raise LookupError("Assistido não encontrado.")

        return CasoJuridicoRepository.listar_por_assistido(
            db, id_assistido
        )

    @staticmethod
    def listar_por_aluno(db: Session, id_usuario: int):
        aluno = AlunoRepository.buscar_por_usuario(db, id_usuario)

        if not aluno:
            raise LookupError("Cadastro de aluno não encontrado.")

        return CasoJuridicoRepository.listar_por_aluno(
            db, aluno.id_aluno
        )

    @staticmethod
    def listar_por_professor(db: Session, id_usuario: int):
        professor = ProfessorRepository.buscar_por_usuario(
            db, id_usuario
        )

        if not professor:
            raise LookupError("Cadastro de professor não encontrado ou inativo.")

        return CasoJuridicoRepository.listar_por_professor(
            db, professor.id_professor
        )

    @staticmethod
    def criar(
        db: Session,
        dados: CasoJuridicoCreate,
        usuario
    ):
        # O caso sempre deve estar vinculado a um assistido existente e ativo.
        assistido = AssistidoRepository.buscar_por_id(
            db, dados.id_assistido
        )

        if not assistido:
            raise LookupError("Assistido não encontrado.")

        if assistido.situacao != "Ativo":
            raise ValueError(
                "Não é possível cadastrar um caso para um assistido inativo."
            )

        codigo_existente = CasoJuridicoRepository.buscar_por_codigo(
            db, dados.codigo_interno
        )

        if codigo_existente:
            raise ValueError("Já existe um caso com esse código interno.")

        dados_caso = dados.model_dump()

        if usuario.perfil == "Aluno":
            aluno = AlunoRepository.buscar_por_usuario(
                db, usuario.id_usuario
            )

            if not aluno:
                raise LookupError("Cadastro de aluno não encontrado.")

            assistido_autorizado = AssistidoRepository.buscar_por_id_e_aluno(
                db,
                dados.id_assistido,
                aluno.id_aluno
            )

            if not assistido_autorizado:
                raise PermissionError(
                    "Você só pode cadastrar casos para assistidos "
                    "vinculados aos seus casos."
                )

            # O servidor determina o responsável e o estado inicial.
            dados_caso["id_aluno_responsavel"] = aluno.id_aluno
            dados_caso["id_professor_orientador"] = None
            dados_caso["situacao"] = "Em triagem"
            dados_caso["data_encerramento"] = None

        elif usuario.perfil != "Gestão":
            raise PermissionError(
                "Somente Aluno ou Gestão podem cadastrar casos jurídicos."
            )

        try:
            caso = CasoJuridicoRepository.criar(
                db,
                CasoJuridicoCreate(**dados_caso)
            )

            db.flush()
            db.refresh(caso)

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
