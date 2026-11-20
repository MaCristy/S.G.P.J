
from sqlalchemy.orm import Session

from app.models.atividade import Atividade
from app.models.caso_juridico import CasoJuridico
from app.schemas.atividade import AtividadeCreate


class AtividadeRepository:

    # Lista todas as atividades, começando pelas mais recentes.
    @staticmethod
    def listar(db: Session):
        return (
            db.query(Atividade)
            .order_by(Atividade.id_atividade.desc())
            .all()
        )

    # Lista as atividades vinculadas aos casos sob responsabilidade do aluno.
    @staticmethod
    def listar_por_aluno(db: Session, id_aluno: int):
        return (
            db.query(Atividade)
            .join(
                CasoJuridico,
                Atividade.id_caso == CasoJuridico.id_caso
            )
            .filter(
                CasoJuridico.id_aluno_responsavel == id_aluno
            )
            .order_by(Atividade.id_atividade.desc())
            .all()
        )

    # Lista as atividades vinculadas aos casos supervisionados pelo professor.
    @staticmethod
    def listar_por_professor(db: Session, id_professor: int):
        return (
            db.query(Atividade)
            .join(
                CasoJuridico,
                Atividade.id_caso == CasoJuridico.id_caso
            )
            .filter(
                CasoJuridico.id_professor_orientador == id_professor
            )
            .order_by(Atividade.id_atividade.desc())
            .all()
        )

    # Busca uma atividade pelo seu identificador.
    @staticmethod
    def buscar_por_id(db: Session, id_atividade: int):
        return (
            db.query(Atividade)
            .filter(Atividade.id_atividade == id_atividade)
            .first()
        )

    # Busca uma atividade vinculada a um caso sob responsabilidade do aluno.
    @staticmethod
    def buscar_por_id_e_aluno(
        db: Session,
        id_atividade: int,
        id_aluno: int
    ):
        return (
            db.query(Atividade)
            .join(
                CasoJuridico,
                Atividade.id_caso == CasoJuridico.id_caso
            )
            .filter(
                Atividade.id_atividade == id_atividade,
                CasoJuridico.id_aluno_responsavel == id_aluno
            )
            .first()
        )

    # Busca uma atividade vinculada a um caso supervisionado pelo professor.
    @staticmethod
    def buscar_por_id_e_professor(
        db: Session,
        id_atividade: int,
        id_professor: int
    ):
        return (
            db.query(Atividade)
            .join(
                CasoJuridico,
                Atividade.id_caso == CasoJuridico.id_caso
            )
            .filter(
                Atividade.id_atividade == id_atividade,
                CasoJuridico.id_professor_orientador == id_professor
            )
            .first()
        )

    # Lista as atividades pertencentes a um caso específico.
    @staticmethod
    def listar_por_caso(db: Session, id_caso: int):
        return (
            db.query(Atividade)
            .filter(Atividade.id_caso == id_caso)
            .order_by(Atividade.id_atividade.desc())
            .all()
        )

    # Lista as atividades atribuídas a um responsável específico.
    @staticmethod
    def listar_por_responsavel(db: Session, id_responsavel: int):
        return (
            db.query(Atividade)
            .filter(Atividade.id_responsavel == id_responsavel)
            .order_by(Atividade.id_atividade.desc())
            .all()
        )

    # Cadastra uma atividade com os dados recebidos.
    @staticmethod
    def criar(db: Session, dados: AtividadeCreate):
        atividade = Atividade(
            id_caso=dados.id_caso,
            titulo=dados.titulo,
            descricao=dados.descricao,
            id_responsavel=dados.id_responsavel,
            situacao=dados.situacao,
            prioridade=dados.prioridade,
            data_prevista=dados.data_prevista
        )

        db.add(atividade)

        return atividade

    # Atualiza os campos informados na atividade existente.
    @staticmethod
    def atualizar(
        db: Session,
        atividade: Atividade,
        dados: dict
    ):
        for campo, valor in dados.items():
            setattr(atividade, campo, valor)

        return atividade
