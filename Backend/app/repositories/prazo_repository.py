
from sqlalchemy.orm import Session

from app.models.prazo import Prazo
from app.models.caso_juridico import CasoJuridico


class PrazoRepository:
    """
    Centraliza as consultas e operações de persistência
    dos prazos vinculados aos casos jurídicos.
    """

    @staticmethod
    def listar(db: Session):
        # Lista todos os prazos, organizados pela data limite mais próxima.
        return (
            db.query(Prazo)
            .order_by(Prazo.data_limite.asc())
            .all()
        )

    @staticmethod
    def listar_por_aluno(db: Session, id_aluno: int):
        # Lista os prazos dos casos atualmente atribuídos ao aluno.
        return (
            db.query(Prazo)
            .join(
                CasoJuridico,
                Prazo.id_caso == CasoJuridico.id_caso
            )
            .filter(
                CasoJuridico.id_aluno_responsavel == id_aluno
            )
            .order_by(Prazo.data_limite.asc())
            .all()
        )

    @staticmethod
    def listar_por_professor(db: Session, id_professor: int):
        # Lista os prazos dos casos supervisionados pelo professor.
        return (
            db.query(Prazo)
            .join(
                CasoJuridico,
                Prazo.id_caso == CasoJuridico.id_caso
            )
            .filter(
                CasoJuridico.id_professor_orientador == id_professor
            )
            .order_by(Prazo.data_limite.asc())
            .all()
        )

    @staticmethod
    def buscar_por_id(db: Session, id_prazo: int):
        # Localiza um prazo pelo seu identificador.
        return (
            db.query(Prazo)
            .filter(Prazo.id_prazo == id_prazo)
            .first()
        )

    @staticmethod
    def buscar_por_id_e_aluno(
        db: Session,
        id_prazo: int,
        id_aluno: int
    ):
        # Verifica se o prazo pertence a um caso atribuído ao aluno.
        return (
            db.query(Prazo)
            .join(
                CasoJuridico,
                Prazo.id_caso == CasoJuridico.id_caso
            )
            .filter(
                Prazo.id_prazo == id_prazo,
                CasoJuridico.id_aluno_responsavel == id_aluno
            )
            .first()
        )

    @staticmethod
    def buscar_por_id_e_professor(
        db: Session,
        id_prazo: int,
        id_professor: int
    ):
        # Verifica se o prazo pertence a um caso supervisionado pelo professor.
        return (
            db.query(Prazo)
            .join(
                CasoJuridico,
                Prazo.id_caso == CasoJuridico.id_caso
            )
            .filter(
                Prazo.id_prazo == id_prazo,
                CasoJuridico.id_professor_orientador == id_professor
            )
            .first()
        )

    @staticmethod
    def listar_por_caso(db: Session, id_caso: int):
        # Lista os prazos vinculados a um caso, em ordem de vencimento.
        return (
            db.query(Prazo)
            .filter(Prazo.id_caso == id_caso)
            .order_by(Prazo.data_limite.asc())
            .all()
        )

    @staticmethod
    def listar_por_responsavel(db: Session, id_responsavel: int):
        # Lista os prazos atribuídos a determinado responsável.
        return (
            db.query(Prazo)
            .filter(Prazo.id_responsavel == id_responsavel)
            .order_by(Prazo.data_limite.asc())
            .all()
        )

    @staticmethod
    def criar(db: Session, dados: dict):
        # Cria o prazo com os dados recebidos do serviço.
        prazo = Prazo(**dados)

        # Persiste o novo registro e atualiza o objeto com os dados do banco.
        db.add(prazo)
        db.commit()
        db.refresh(prazo)

        return prazo

    @staticmethod
    def atualizar(db: Session, prazo: Prazo, dados: dict):
        # Atualiza somente os campos recebidos.
        for campo, valor in dados.items():
            setattr(prazo, campo, valor)

        # Salva as alterações e atualiza o objeto com os dados persistidos.
        db.commit()
        db.refresh(prazo)

        return prazo
