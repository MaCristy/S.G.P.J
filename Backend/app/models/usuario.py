
from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(150), nullable=False)
    email_institucional = Column(String(150), nullable=False, unique=True)
    senha_armazenada = Column(String(255), nullable=False)
    perfil = Column(String(50), nullable=False)
    situacao_conta = Column(
        String(30),
        nullable=False,
        server_default="Ativo"
    )
    data_criacao = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )
    ultimo_acesso = Column(DateTime, nullable=True)
