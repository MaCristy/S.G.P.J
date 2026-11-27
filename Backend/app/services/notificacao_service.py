
from sqlalchemy.orm import Session

from app.repositories.notificacao_repository import NotificacaoRepository


class NotificacaoService:

    @staticmethod
    def listar_por_usuario(db: Session, id_usuario: int):
        return NotificacaoRepository.listar_por_usuario(
            db,
            id_usuario
        )

    @staticmethod
    def contar_nao_lidas(db: Session, id_usuario: int):
        return NotificacaoRepository.contar_nao_lidas(
            db,
            id_usuario
        )

    @staticmethod
    def marcar_como_lida(
        db: Session,
        id_notificacao: int,
        id_usuario: int
    ):
        notificacao = NotificacaoRepository.buscar_por_id(
            db,
            id_notificacao,
            id_usuario
        )

        if notificacao is None:
            return None

        if not notificacao.lida:
            return NotificacaoRepository.marcar_como_lida(
                db,
                notificacao
            )

        return notificacao

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
        return NotificacaoRepository.criar(
            db=db,
            id_usuario_destinatario=id_usuario_destinatario,
            tipo=tipo,
            titulo=titulo,
            mensagem=mensagem,
            id_usuario_origem=id_usuario_origem,
            id_caso=id_caso,
            link=link
        )
