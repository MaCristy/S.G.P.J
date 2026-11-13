
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate


class UsuarioRepository:

    @staticmethod
    def listar(db: Session):
        return db.query(Usuario).order_by(Usuario.nome).all()

    @staticmethod
    def buscar_por_id(db: Session, id_usuario: int):
        return db.query(Usuario).filter(
            Usuario.id_usuario == id_usuario
        ).first()

    @staticmethod
    def buscar_por_email(db: Session, email: str):
        return db.query(Usuario).filter(
            Usuario.email_institucional == email
        ).first()

    @staticmethod
    def criar(db: Session, dados: UsuarioCreate, senha_hash: str):
        usuario = Usuario(
            nome=dados.nome,
            email_institucional=dados.email_institucional,
            senha_armazenada=senha_hash,
            perfil=dados.perfil
        )

        db.add(usuario)
        return usuario
