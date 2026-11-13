
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.prazo import (
    PrazoCreate,
    PrazoUpdate,
    PrazoResponse
)
from app.services.prazo_service import PrazoService


router = APIRouter(
    prefix="/prazos",
    tags=["Prazos"]
)


@router.get("/", response_model=list[PrazoResponse])
def listar_prazos(db: Session = Depends(get_db)):
    return PrazoService.listar(db)


@router.get("/caso/{id_caso}", response_model=list[PrazoResponse])
def listar_prazos_por_caso(
    id_caso: int,
    db: Session = Depends(get_db)
):
    return PrazoService.listar_por_caso(db, id_caso)


@router.get(
    "/responsavel/{id_responsavel}",
    response_model=list[PrazoResponse]
)
def listar_prazos_por_responsavel(
    id_responsavel: int,
    db: Session = Depends(get_db)
):
    return PrazoService.listar_por_responsavel(
        db, id_responsavel
    )


@router.get("/{id_prazo}", response_model=PrazoResponse)
def buscar_prazo(
    id_prazo: int,
    db: Session = Depends(get_db)
):
    try:
        return PrazoService.buscar_por_id(db, id_prazo)

    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )


@router.post(
    "/",
    response_model=PrazoResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_prazo(
    dados: PrazoCreate,
    db: Session = Depends(get_db)
):
    try:
        return PrazoService.criar(db, dados)

    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )


@router.patch("/{id_prazo}", response_model=PrazoResponse)
def atualizar_prazo(
    id_prazo: int,
    dados: PrazoUpdate,
    db: Session = Depends(get_db)
):
    try:
        return PrazoService.atualizar(
            db, id_prazo, dados
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
