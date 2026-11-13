
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.assistido import (
    AssistidoCreate,
    AssistidoUpdate,
    AssistidoResponse
)
from app.services.assistido import AssistidoService


router = APIRouter(
    prefix="/assistidos",
    tags=["Assistidos"]
)


@router.get(
    "/",
    response_model=list[AssistidoResponse],
    status_code=status.HTTP_200_OK
)
def listar_assistidos(db: Session = Depends(get_db)):
    return AssistidoService.listar(db)


@router.get(
    "/{id_assistido}",
    response_model=AssistidoResponse,
    status_code=status.HTTP_200_OK
)
def buscar_assistido(
    id_assistido: int,
    db: Session = Depends(get_db)
):
    try:
        return AssistidoService.buscar_por_id(db, id_assistido)

    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )


@router.post(
    "/",
    response_model=AssistidoResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_assistido(
    dados: AssistidoCreate,
    db: Session = Depends(get_db)
):
    try:
        return AssistidoService.criar(db, dados)

    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(erro)
        )


@router.patch(
    "/{id_assistido}",
    response_model=AssistidoResponse,
    status_code=status.HTTP_200_OK
)
def atualizar_assistido(
    id_assistido: int,
    dados: AssistidoUpdate,
    db: Session = Depends(get_db)
):
    try:
        return AssistidoService.atualizar(
            db,
            id_assistido,
            dados
        )

    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )

    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(erro)
        )
