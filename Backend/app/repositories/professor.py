
from sqlalchemy.orm import Session

from app.models.professor import Professor
from app.schemas.professor import ProfessorCreate


class ProfessorRepository:
    """
    Centraliza as consultas e operações de persistência
    dos dados dos professores e orientadores.
    """

    @staticmethod
    def listar(db: Session):
        # Lista os professores, começando pelos registros mais recentes.
        return (
            db.query(Professor)
            .order_by(Professor.id_professor.desc())
            .all()
        )

    @staticmethod
    def buscar_por_id(db: Session, id_professor: int):
        # Localiza um professor pelo identificador do seu cadastro.
        return (
            db.query(Professor)
            .filter(Professor.id_professor == id_professor)
            .first()
        )

    @staticmethod
    def buscar_por_usuario(db: Session, id_usuario: int):
        # Localiza o cadastro de professor vinculado a um usuário do sistema.
        return (
            db.query(Professor)
            .filter(Professor.id_usuario == id_usuario)
            .first()
        )

    @staticmethod
    def buscar_por_identificacao(db: Session, identificacao: str):
        # Busca um professor pela sua identificação funcional.
        return (
            db.query(Professor)
            .filter(
                Professor.identificacao_funcional == identificacao
            )
            .first()
        )

    @staticmethod
    def criar(db: Session, dados: ProfessorCreate):
        # Cria o cadastro utilizando os dados validados pelo schema.
        professor = Professor(
            id_usuario=dados.id_usuario,
            identificacao_funcional=dados.identificacao_funcional,
            area_vinculo=dados.area_vinculo,
            situacao=dados.situacao
        )

        # Adiciona o novo professor à sessão do banco de dados.
        db.add(professor)

        return professor

    @staticmethod
    def atualizar(db: Session, professor: Professor, dados: dict):
        # Atualiza somente os atributos enviados pelo serviço.
        for campo, valor in dados.items():
            setattr(professor, campo, valor)

        return professor
