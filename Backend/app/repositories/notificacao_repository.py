
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.notificacao import Notificacao


class NotificacaoRepository:

    @staticmethod
    def listar_por_usuario(db: Session, id_usuario: int):
        return (
            db.query(Notificacao)
            .filter(
                Notificacao.id_usuario_destinatario == id_usuario
            )
            .order_by(Notificacao.data_criacao.desc())
            .all()
        )

    @staticmethod
    def contar_nao_lidas(db: Session, id_usuario: int):
        return (
            db.query(Notificacao)
            .filter(
                Notificacao.id_usuario_destinatario == id_usuario,
                Notificacao.lida == False
            )
            .count()
        )

    @staticmethod
    def buscar_por_id(
        db: Session,
        id_notificacao: int,
        id_usuario: int
    ):
        return (
            db.query(Notificacao)
            .filter(
                Notificacao.id_notificacao == id_notificacao,
                Notificacao.id_usuario_destinatario == id_usuario
            )
            .first()
        )

    @staticmethod
    def criar(
        db: Session,
        id_usuario_destinatario: int,
        tipo: str,
        titulo: str,
        mensagem: str,
        id_usuario_origem: int | None = None,
        id_caso: int | None = None,
        link: str | None = None
    ):
        notificacao = Notificacao(
            id_usuario_destinatario=id_usuario_destinatario,
            id_usuario_origem=id_usuario_origem,
            id_caso=id_caso,
            tipo=tipo,
            titulo=titulo,
            mensagem=mensagem,
            link=link
        )

        db.add(notificacao)
        db.commit()
        db.refresh(notificacao)

        return notificacao

    @staticmethod
    def marcar_como_lida(db: Session, notificacao: Notificacao):
        notificacao.lida = True
        notificacao.data_leitura = datetime.now()

        db.commit()
        db.refresh(notificacao)

        return notificacao
