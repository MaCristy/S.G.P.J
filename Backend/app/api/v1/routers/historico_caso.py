
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.historico_caso import (
    HistoricoCasoCreate,
    HistoricoCasoResponse
)
from app.services.historico_caso_service import (
    HistoricoCasoService
)


router = APIRouter(
    prefix="/historico-casos",
    tags=["Histórico de Casos"]
)


@router.get("/", response_model=list[HistoricoCasoResponse])
def listar_historico(db: Session = Depends(get_db)):
    return HistoricoCasoService.listar(db)


@router.get(
    "/caso/{id_caso}",
    response_model=list[HistoricoCasoResponse]
)
def listar_historico_por_caso(
    id_caso: int,
    db: Session = Depends(get_db)
):
    return HistoricoCasoService.listar_por_caso(
        db, id_caso
    )


@router.get(
    "/usuario/{id_usuario_responsavel}",
    response_model=list[HistoricoCasoResponse]
)
def listar_historico_por_usuario(
    id_usuario_responsavel: int,
    db: Session = Depends(get_db)
):
    return HistoricoCasoService.listar_por_usuario(
        db, id_usuario_responsavel
    )


@router.get(
    "/{id_historico}",
    response_model=HistoricoCasoResponse
)
def buscar_historico(
    id_historico: int,
    db: Session = Depends(get_db)
):
    try:
        return HistoricoCasoService.buscar_por_id(
            db, id_historico
        )

    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )


@router.post(
    "/",
    response_model=HistoricoCasoResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_historico(
    dados: HistoricoCasoCreate,
    db: Session = Depends(get_db)
):
    try:
        return HistoricoCasoService.criar(db, dados)

    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )
