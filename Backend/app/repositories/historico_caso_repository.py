
from sqlalchemy.orm import Session

from app.models.historico_caso import HistoricoCaso
from app.models.caso_juridico import CasoJuridico


class HistoricoCasoRepository:
    """
    Centraliza as consultas e operações de persistência
    dos registros de histórico dos casos jurídicos.
    """

    @staticmethod
    def listar(db: Session):
        # Lista todos os registros de histórico, do mais recente ao mais antigo.
        return (
            db.query(HistoricoCaso)
            .order_by(HistoricoCaso.data_hora.desc())
            .all()
        )

    @staticmethod
    def listar_por_aluno(db: Session, id_aluno: int):
        # Busca os históricos dos casos atualmente atribuídos ao aluno.
        return (
            db.query(HistoricoCaso)
            .join(
                CasoJuridico,
                HistoricoCaso.id_caso == CasoJuridico.id_caso
            )
            .filter(
                CasoJuridico.id_aluno_responsavel == id_aluno
            )
            .order_by(HistoricoCaso.data_hora.desc())
            .all()
        )

    @staticmethod
    def listar_por_professor(db: Session, id_professor: int):
        # Busca os históricos dos casos supervisionados pelo professor.
        return (
            db.query(HistoricoCaso)
            .join(
                CasoJuridico,
                HistoricoCaso.id_caso == CasoJuridico.id_caso
            )
            .filter(
                CasoJuridico.id_professor_orientador == id_professor
            )
            .order_by(HistoricoCaso.data_hora.desc())
            .all()
        )

    @staticmethod
    def buscar_por_id(db: Session, id_historico: int):
        # Localiza um registro de histórico pelo seu identificador.
        return (
            db.query(HistoricoCaso)
            .filter(
                HistoricoCaso.id_historico == id_historico
            )
            .first()
        )

    @staticmethod
    def buscar_por_id_e_aluno(
        db: Session,
        id_historico: int,
        id_aluno: int
    ):
        # Verifica se o histórico pertence a um caso atribuído ao aluno.
        return (
            db.query(HistoricoCaso)
            .join(
                CasoJuridico,
                HistoricoCaso.id_caso == CasoJuridico.id_caso
            )
            .filter(
                HistoricoCaso.id_historico == id_historico,
                CasoJuridico.id_aluno_responsavel == id_aluno
            )
            .first()
        )

    @staticmethod
    def buscar_por_id_e_professor(
        db: Session,
        id_historico: int,
        id_professor: int
    ):
        # Verifica se o histórico pertence a um caso supervisionado pelo professor.
        return (
            db.query(HistoricoCaso)
            .join(
                CasoJuridico,
                HistoricoCaso.id_caso == CasoJuridico.id_caso
            )
            .filter(
                HistoricoCaso.id_historico == id_historico,
                CasoJuridico.id_professor_orientador == id_professor
            )
            .first()
        )

    @staticmethod
    def listar_por_caso(db: Session, id_caso: int):
        # Lista os registros associados a um caso em ordem cronológica decrescente.
        return (
            db.query(HistoricoCaso)
            .filter(HistoricoCaso.id_caso == id_caso)
            .order_by(HistoricoCaso.data_hora.desc())
            .all()
        )

    @staticmethod
    def listar_por_usuario(
        db: Session,
        id_usuario_responsavel: int
    ):
        # Lista as ocorrências registradas por determinado usuário.
        return (
            db.query(HistoricoCaso)
            .filter(
                HistoricoCaso.id_usuario_responsavel
                == id_usuario_responsavel
            )
            .order_by(HistoricoCaso.data_hora.desc())
            .all()
        )

    @staticmethod
    def criar(db: Session, dados: dict):
        # Cria a ocorrência com os dados recebidos do serviço.
        historico = HistoricoCaso(**dados)

        # Persiste o registro e atualiza o objeto com os dados gerados pelo banco.
        db.add(historico)
        db.commit()
        db.refresh(historico)

        return historico
