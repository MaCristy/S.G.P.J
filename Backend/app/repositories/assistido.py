
from sqlalchemy.orm import Session

from app.models.caso_juridico import CasoJuridico
from app.models.assistido import Assistido
from app.schemas.assistido import AssistidoCreate, AssistidoUpdate


class AssistidoRepository:
    """Responsável pelo acesso aos dados dos assistidos."""

    # Lista todos os assistidos, ordenados pelo nome.
    @staticmethod
    def listar(db: Session):
        return (
            db.query(Assistido)
            .order_by(Assistido.nome_completo.asc())
            .all()
        )

    # Lista os assistidos que possuem casos sob responsabilidade do aluno.
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
            # Evita repetir assistidos que possuem mais de um caso com o aluno.
            .distinct()
            .order_by(Assistido.nome_completo.asc())
            .all()
        )

    # Lista os assistidos que possuem casos supervisionados pelo professor.
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
            # Evita repetir assistidos que possuem mais de um caso com o professor.
            .distinct()
            .order_by(Assistido.nome_completo.asc())
            .all()
        )

    # Busca um assistido quando ele possui vínculo com um caso do aluno.
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

    # Busca um assistido quando ele possui vínculo com um caso supervisionado pelo professor.
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

    # Busca um assistido pelo seu identificador.
    @staticmethod
    def buscar_por_id(db: Session, id_assistido: int):
        return (
            db.query(Assistido)
            .filter(Assistido.id_assistido == id_assistido)
            .first()
        )

    # Busca um assistido pelo identificador cadastral.
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

    # Cadastra um assistido e atualiza seus dados na sessão do banco.
    @staticmethod
    def criar(db: Session, dados: AssistidoCreate):
        assistido = Assistido(**dados.model_dump())

        db.add(assistido)
        db.flush()
        db.refresh(assistido)

        return assistido

    # Atualiza somente os campos enviados na solicitação.
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
