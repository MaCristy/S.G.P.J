
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.assistido import AssistidoRepository
from app.schemas.assistido import AssistidoCreate, AssistidoUpdate


class AssistidoService:
    """Contém as regras de negócio dos assistidos."""

    @staticmethod
    def listar(db: Session):
        return AssistidoRepository.listar(db)

    @staticmethod
    def buscar_por_id(db: Session, id_assistido: int):
        assistido = AssistidoRepository.buscar_por_id(
            db,
            id_assistido
        )

        if not assistido:
            raise LookupError("Assistido não encontrado.")

        return assistido

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

        try:
            assistido = AssistidoRepository.criar(db, dados)
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

    @staticmethod
    def atualizar(
        db: Session,
        id_assistido: int,
        dados: AssistidoUpdate
    ):
        assistido = AssistidoRepository.buscar_por_id(
            db,
            id_assistido
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
