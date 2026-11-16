
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.atendimento import (
    AtendimentoCreate,
    AtendimentoResponse
)
from app.services.atendimento import AtendimentoService
from app.models.usuario import Usuario


router = APIRouter(
    prefix="/atendimentos",
    tags=["Atendimentos"]
)



@router.get(
    "/",
    response_model=list[AtendimentoResponse],
    status_code=status.HTTP_200_OK
)
def listar_atendimentos(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        if usuario_atual.perfil == "Gestão":
            return AtendimentoService.listar(db)

        if usuario_atual.perfil == "Aluno":
            return AtendimentoService.listar_por_aluno(
                db,
                usuario_atual.id_usuario
            )

        if usuario_atual.perfil == "Professor":
            return AtendimentoService.listar_por_professor(
                db,
                usuario_atual.id_usuario
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para listar atendimentos."
        )

    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )

    except PermissionError as erro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )



@router.get(
    "/assistido/{id_assistido}",
    response_model=list[AtendimentoResponse],
    status_code=status.HTTP_200_OK
)
def listar_atendimentos_por_assistido(
    id_assistido: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        if usuario_atual.perfil == "Gestão":
            return AtendimentoService.listar_por_assistido(
                db, id_assistido
            )

        if usuario_atual.perfil == "Aluno":
            return AtendimentoService.listar_por_assistido_e_aluno(
                db,
                id_assistido,
                usuario_atual.id_usuario
            )

        if usuario_atual.perfil == "Professor":
            return AtendimentoService.listar_por_assistido_e_professor(
                db,
                id_assistido,
                usuario_atual.id_usuario
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para consultar atendimentos."
        )

    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )

    except PermissionError as erro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )




@router.get(
    "/{id_atendimento}",
    response_model=AtendimentoResponse,
    status_code=status.HTTP_200_OK
)
def buscar_atendimento(
    id_atendimento: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        if usuario_atual.perfil == "Gestão":
            return AtendimentoService.buscar_por_id(
                db, id_atendimento
            )

        if usuario_atual.perfil == "Aluno":
            return AtendimentoService.buscar_por_id_e_aluno(
                db,
                id_atendimento,
                usuario_atual.id_usuario
            )

        if usuario_atual.perfil == "Professor":
            return AtendimentoService.buscar_por_id_e_professor(
                db,
                id_atendimento,
                usuario_atual.id_usuario
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para consultar este atendimento."
        )

    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )

    except PermissionError as erro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )



@router.post(
    "/",
    response_model=AtendimentoResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_atendimento(
    dados: AtendimentoCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        return AtendimentoService.criar(
            db,
            dados,
            usuario_atual.id_usuario,
            usuario_atual.perfil
        )

    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )

    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )

    except PermissionError as erro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )
