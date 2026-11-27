
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Dependências para acesso ao banco e identificação do usuário autenticado.
from app.api.deps import get_db, get_current_user
from app.models.usuario import Usuario

# Schema utilizado na resposta das notificações.
from app.schemas.notificacao import NotificacaoResponse

# Serviço responsável pelas regras de negócio das notificações.
from app.services.notificacao_service import NotificacaoService


# Configuração das rotas de notificações.
router = APIRouter(
    prefix="/notificacoes",
    tags=["Notificações"]
)


# Lista as notificações do usuário autenticado.
@router.get("/", response_model=list[NotificacaoResponse])
def listar_notificacoes(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    return NotificacaoService.listar_por_usuario(
        db,
        usuario.id_usuario
    )


# Retorna a quantidade de notificações não lidas.
@router.get("/nao-lidas")
def contar_notificacoes_nao_lidas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    total = NotificacaoService.contar_nao_lidas(
        db,
        usuario.id_usuario
    )

    return {
        "total": total
    }


# Marca uma notificação como lida.
@router.patch(
    "/{id_notificacao}/lida",
    response_model=NotificacaoResponse
)
def marcar_notificacao_como_lida(
    id_notificacao: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    notificacao = NotificacaoService.marcar_como_lida(
        db,
        id_notificacao,
        usuario.id_usuario
    )

    if notificacao is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada."
        )

    return notificacao
