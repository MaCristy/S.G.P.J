
from sqlalchemy.orm import Session

from app.models.caso_juridico import CasoJuridico
from app.schemas.caso_juridico import CasoJuridicoCreate


class CasoJuridicoRepository:

    # Lista todos os casos jurídicos, começando pelos mais recentes.
    @staticmethod
    def listar(db: Session):
        return (
            db.query(CasoJuridico)
            .order_by(CasoJuridico.id_caso.desc())
            .all()
        )

    # Busca um caso jurídico pelo seu identificador.
    @staticmethod
    def buscar_por_id(db: Session, id_caso: int):
        return (
            db.query(CasoJuridico)
            .filter(CasoJuridico.id_caso == id_caso)
            .first()
        )

    # Busca um caso jurídico pelo código interno.
    @staticmethod
    def buscar_por_codigo(db: Session, codigo_interno: str):
        return (
            db.query(CasoJuridico)
            .filter(CasoJuridico.codigo_interno == codigo_interno)
            .first()
        )

    # Lista os casos jurídicos vinculados a um assistido.
    @staticmethod
    def listar_por_assistido(db: Session, id_assistido: int):
        return (
            db.query(CasoJuridico)
            .filter(CasoJuridico.id_assistido == id_assistido)
            .order_by(CasoJuridico.id_caso.desc())
            .all()
        )

    # Lista os casos sob responsabilidade de um aluno.
    @staticmethod
    def listar_por_aluno(db: Session, id_aluno: int):
        return (
            db.query(CasoJuridico)
            .filter(
                CasoJuridico.id_aluno_responsavel == id_aluno
            )
            .order_by(CasoJuridico.id_caso.desc())
            .all()
        )

    # Lista os casos supervisionados por um professor.
    @staticmethod
    def listar_por_professor(db: Session, id_professor: int):
        return (
            db.query(CasoJuridico)
            .filter(
                CasoJuridico.id_professor_orientador == id_professor
            )
            .order_by(CasoJuridico.id_caso.desc())
            .all()
        )

    # Cadastra um novo caso jurídico com os dados recebidos.
    @staticmethod
    def criar(db: Session, dados: CasoJuridicoCreate):
        caso = CasoJuridico(**dados.model_dump())

        db.add(caso)
        return caso

    # Atualiza os campos informados no caso jurídico existente.
    @staticmethod
    def atualizar(db: Session, caso: CasoJuridico, dados: dict):
        for campo, valor in dados.items():
            setattr(caso, campo, valor)

        return caso
