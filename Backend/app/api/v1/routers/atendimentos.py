
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.atendimento import (
    AtendimentoCreate,
    AtendimentoResponse
)
from app.services.atendimento import AtendimentoService


router = APIRouter(
    prefix="/atendimentos",
    tags=["Atendimentos"]
)


@router.get(
    "/",
    response_model=list[AtendimentoResponse],
    status_code=status.HTTP_200_OK
)
def listar_atendimentos(db: Session = Depends(get_db)):
    return AtendimentoService.listar(db)


@router.get(
    "/assistido/{id_assistido}",
    response_model=list[AtendimentoResponse],
    status_code=status.HTTP_200_OK
)
def listar_atendimentos_por_assistido(
    id_assistido: int,
    db: Session = Depends(get_db)
):
    try:
        return AtendimentoService.listar_por_assistido(
            db, id_assistido
        )
    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )


@router.get(
    "/{id_atendimento}",
    response_model=AtendimentoResponse,
    status_code=status.HTTP_200_OK
)
def buscar_atendimento(
    id_atendimento: int,
    db: Session = Depends(get_db)
):
    try:
        return AtendimentoService.buscar_por_id(
            db, id_atendimento
        )
    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )


@router.post(
    "/",
    response_model=AtendimentoResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_atendimento(
    dados: AtendimentoCreate,
    db: Session = Depends(get_db)
):
    try:
        return AtendimentoService.criar(db, dados)

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
