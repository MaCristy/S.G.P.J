
from sqlalchemy.orm import Session

from app.models.assistido import Assistido
from app.schemas.assistido import AssistidoCreate, AssistidoUpdate


class AssistidoRepository:
    """Responsável pelo acesso aos dados dos assistidos."""

    @staticmethod
    def listar(db: Session):
        return (
            db.query(Assistido)
            .order_by(Assistido.nome_completo.asc())
            .all()
        )

    @staticmethod
    def buscar_por_id(db: Session, id_assistido: int):
        return (
            db.query(Assistido)
            .filter(Assistido.id_assistido == id_assistido)
            .first()
        )

    @staticmethod
    def buscar_por_identificador(
        db: Session,
        identificador_cadastral: str
    ):
        return (
            db.query(Assistido)
            .filter(
                Assistido.identificador_cadastral
                == identificador_cadastral
            )
            .first()
        )

    @staticmethod
    def criar(db: Session, dados: AssistidoCreate):
        assistido = Assistido(**dados.model_dump())

        db.add(assistido)
        db.flush()
        db.refresh(assistido)

        return assistido

    @staticmethod
    def atualizar(
        db: Session,
        assistido: Assistido,
        dados: AssistidoUpdate
    ):
        dados_atualizados = dados.model_dump(exclude_unset=True)

        for campo, valor in dados_atualizados.items():
            setattr(assistido, campo, valor)

        db.flush()
        db.refresh(assistido)

        return assistido
