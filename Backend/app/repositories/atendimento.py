
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.atendimento import Atendimento
from app.models.caso_juridico import CasoJuridico
from app.schemas.atendimento import AtendimentoCreate


class AtendimentoRepository:

    # Lista todos os atendimentos, começando pelos mais recentes.
    @staticmethod
    def listar(db: Session):
        return (
            db.query(Atendimento)
            .order_by(Atendimento.data_hora.desc())
            .all()
        )

    # Busca um atendimento pelo seu identificador.
    @staticmethod
    def buscar_por_id(db: Session, id_atendimento: int):
        return (
            db.query(Atendimento)
            .filter(Atendimento.id_atendimento == id_atendimento)
            .first()
        )

    # Lista os atendimentos vinculados a um assistido.
    @staticmethod
    def listar_por_assistido(db: Session, id_assistido: int):
        return (
            db.query(Atendimento)
            .filter(Atendimento.id_assistido == id_assistido)
            .order_by(Atendimento.data_hora.desc())
            .all()
        )

    # Lista atendimentos do assistido relacionados ao aluno ou registrados por ele.
    @staticmethod
    def listar_por_assistido_e_aluno(
        db: Session,
        id_assistido: int,
        id_aluno: int,
        id_usuario: int
    ):
        return (
            db.query(Atendimento)
            .outerjoin(
                CasoJuridico,
                Atendimento.id_caso == CasoJuridico.id_caso
            )
            .filter(
                Atendimento.id_assistido == id_assistido,
                or_(
                    CasoJuridico.id_aluno_responsavel == id_aluno,
                    Atendimento.id_usuario_registro == id_usuario
                )
            )
            .order_by(Atendimento.data_hora.desc())
            .all()
        )

    # Lista atendimentos associados aos casos do aluno ou registrados por ele.
    @staticmethod
    def listar_por_aluno(
        db: Session,
        id_aluno: int,
        id_usuario: int
    ):
        return (
            db.query(Atendimento)
            .outerjoin(
                CasoJuridico,
                Atendimento.id_caso == CasoJuridico.id_caso
            )
            .filter(
                or_(
                    CasoJuridico.id_aluno_responsavel == id_aluno,
                    Atendimento.id_usuario_registro == id_usuario
                )
            )
            .order_by(Atendimento.data_hora.desc())
            .all()
        )

    # Lista os atendimentos vinculados aos casos supervisionados pelo professor.
    @staticmethod
    def listar_por_professor(db: Session, id_professor: int):
        return (
            db.query(Atendimento)
            .join(
                CasoJuridico,
                Atendimento.id_caso == CasoJuridico.id_caso
            )
            .filter(
                CasoJuridico.id_professor_orientador == id_professor
            )
            .order_by(Atendimento.data_hora.desc())
            .all()
        )

    # Busca um atendimento acessível ao aluno por responsabilidade ou autoria do registro.
    @staticmethod
    def buscar_por_id_e_aluno(
        db: Session,
        id_atendimento: int,
        id_aluno: int,
        id_usuario: int
    ):
        return (
            db.query(Atendimento)
            .outerjoin(
                CasoJuridico,
                Atendimento.id_caso == CasoJuridico.id_caso
            )
            .filter(
                Atendimento.id_atendimento == id_atendimento,
                or_(
                    CasoJuridico.id_aluno_responsavel == id_aluno,
                    Atendimento.id_usuario_registro == id_usuario
                )
            )
            .first()
        )

    # Busca um atendimento vinculado a um caso supervisionado pelo professor.
    @staticmethod
    def buscar_por_id_e_professor(
        db: Session,
        id_atendimento: int,
        id_professor: int
    ):
        return (
            db.query(Atendimento)
            .join(
                CasoJuridico,
                Atendimento.id_caso == CasoJuridico.id_caso
            )
            .filter(
                Atendimento.id_atendimento == id_atendimento,
                CasoJuridico.id_professor_orientador == id_professor
            )
            .first()
        )

    # Cadastra um atendimento associando-o ao usuário que realizou o registro.
    @staticmethod
    def criar(
        db: Session,
        dados: AtendimentoCreate,
        id_usuario_registro: int
    ):
        dados_atendimento = dados.model_dump()
        dados_atendimento["id_usuario_registro"] = id_usuario_registro

        atendimento = Atendimento(**dados_atendimento)

        db.add(atendimento)
        db.flush()
        db.refresh(atendimento)

        return atendimento
