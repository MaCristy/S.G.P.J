
from sqlalchemy.orm import Session

from app.models.caso_juridico import CasoJuridico
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
    def listar_por_aluno(db: Session, id_aluno: int):
        return (
            db.query(Assistido)
            .join(
                CasoJuridico,
                CasoJuridico.id_assistido == Assistido.id_assistido
            )
            .filter(
                CasoJuridico.id_aluno_responsavel == id_aluno
            )
            .distinct()
            .order_by(Assistido.nome_completo.asc())
            .all()
        )

    @staticmethod
    def listar_por_professor(db: Session, id_professor: int):
        return (
            db.query(Assistido)
            .join(
                CasoJuridico,
                CasoJuridico.id_assistido == Assistido.id_assistido
            )
            .filter(
                CasoJuridico.id_professor_orientador == id_professor
            )
            .distinct()
            .order_by(Assistido.nome_completo.asc())
            .all()
        )

    
    @staticmethod
    def buscar_por_id_e_aluno(
        db: Session,
        id_assistido: int,
        id_aluno: int
    ):
        return (
            db.query(Assistido)
            .join(
                CasoJuridico,
                CasoJuridico.id_assistido == Assistido.id_assistido
            )
            .filter(
                Assistido.id_assistido == id_assistido,
                CasoJuridico.id_aluno_responsavel == id_aluno
            )
            .first()
        )

    @staticmethod
    def buscar_por_id_e_professor(
        db: Session,
        id_assistido: int,
        id_professor: int
    ):
        return (
            db.query(Assistido)
            .join(
                CasoJuridico,
                CasoJuridico.id_assistido == Assistido.id_assistido
            )
            .filter(
                Assistido.id_assistido == id_assistido,
                CasoJuridico.id_professor_orientador == id_professor
            )
            .first()
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
