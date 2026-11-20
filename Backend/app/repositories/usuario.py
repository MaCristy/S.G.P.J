
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate


class UsuarioRepository:
    """
    Centraliza as consultas e operações de persistência
    dos usuários do sistema.
    """

    @staticmethod
    def listar(db: Session):
        # Lista os usuários em ordem alfabética pelo nome.
        return db.query(Usuario).order_by(Usuario.nome).all()

    @staticmethod
    def buscar_por_id(db: Session, id_usuario: int):
        # Localiza um usuário pelo seu identificador.
        return db.query(Usuario).filter(
            Usuario.id_usuario == id_usuario
        ).first()

    @staticmethod
    def buscar_por_email(db: Session, email: str):
        # Localiza um usuário pelo e-mail institucional.
        return db.query(Usuario).filter(
            Usuario.email_institucional == email
        ).first()

    @staticmethod
    def criar(db: Session, dados: UsuarioCreate, senha_hash: str):
        # Cria o usuário utilizando a senha já criptografada.
        usuario = Usuario(
            nome=dados.nome,
            email_institucional=dados.email_institucional,
            senha_armazenada=senha_hash,
            perfil=dados.perfil
        )

        # Adiciona o novo usuário à sessão do banco de dados.
        db.add(usuario)
        return usuario

    @staticmethod
    def atualizar(db: Session, usuario: Usuario, dados: dict):
        # Atualiza somente os campos enviados pelo serviço.
        for campo, valor in dados.items():
            setattr(usuario, campo, valor)

        # Mantém o objeto associado à sessão do banco de dados.
        db.add(usuario)
        return usuario
