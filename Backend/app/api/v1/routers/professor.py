
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.professor import (
    ProfessorCreate,
    ProfessorUpdate,
    ProfessorResponse
)
from app.services.professor import ProfessorService


router = APIRouter(
    prefix="/professores",
    tags=["Professores/Orientadores"]
)


@router.get("/", response_model=list[ProfessorResponse])
def listar_professores(db: Session = Depends(get_db)):
    return ProfessorService.listar(db)


@router.get("/{id_professor}", response_model=ProfessorResponse)
def buscar_professor(
    id_professor: int,
    db: Session = Depends(get_db)
):
    try:
        return ProfessorService.buscar_por_id(db, id_professor)

    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )


@router.post(
    "/",
    response_model=ProfessorResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_professor(
    dados: ProfessorCreate,
    db: Session = Depends(get_db)
):
    try:
        return ProfessorService.criar(db, dados)

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


@router.patch("/{id_professor}", response_model=ProfessorResponse)
def atualizar_professor(
    id_professor: int,
    dados: ProfessorUpdate,
    db: Session = Depends(get_db)
):
    try:
        return ProfessorService.atualizar(
            db, id_professor, dados
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
