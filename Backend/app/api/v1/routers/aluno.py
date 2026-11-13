
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.aluno import (
    AlunoCreate,
    AlunoUpdate,
    AlunoResponse
)
from app.services.aluno import AlunoService


router = APIRouter(
    prefix="/alunos",
    tags=["Alunos/Estagiários"]
)


@router.get("/", response_model=list[AlunoResponse])
def listar_alunos(db: Session = Depends(get_db)):
    return AlunoService.listar(db)


@router.get("/{id_aluno}", response_model=AlunoResponse)
def buscar_aluno(
    id_aluno: int,
    db: Session = Depends(get_db)
):
    try:
        return AlunoService.buscar_por_id(db, id_aluno)

    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )


@router.post(
    "/",
    response_model=AlunoResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_aluno(
    dados: AlunoCreate,
    db: Session = Depends(get_db)
):
    try:
        return AlunoService.criar(db, dados)

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


@router.patch("/{id_aluno}", response_model=AlunoResponse)
def atualizar_aluno(
    id_aluno: int,
    dados: AlunoUpdate,
    db: Session = Depends(get_db)
):
    try:
        return AlunoService.atualizar(db, id_aluno, dados)

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
