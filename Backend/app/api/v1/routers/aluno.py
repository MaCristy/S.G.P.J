
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, check_role
from app.models.usuario import Usuario
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


@router.get(
    "/",
    response_model=list[AlunoResponse],
    status_code=status.HTTP_200_OK
)
def listar_alunos(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        if usuario_atual.perfil == "Gestão":
            return AlunoService.listar(db)

        if usuario_atual.perfil == "Professor":
            return AlunoService.listar_por_professor(
                db, usuario_atual.id_usuario
            )

        if usuario_atual.perfil == "Aluno":
            aluno = AlunoService.buscar_por_usuario(
                db, usuario_atual.id_usuario
            )
            return [aluno]

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para listar alunos."
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
    "/{id_aluno}",
    response_model=AlunoResponse,
    status_code=status.HTTP_200_OK
)
def buscar_aluno(
    id_aluno: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        aluno = AlunoService.buscar_por_id(db, id_aluno)

        if usuario_atual.perfil == "Gestão":
            return aluno

        if usuario_atual.perfil == "Aluno":
            aluno_atual = AlunoService.buscar_por_usuario(
                db, usuario_atual.id_usuario
            )

            if aluno.id_aluno != aluno_atual.id_aluno:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Você só pode consultar seu próprio cadastro."
                )

            return aluno

        if usuario_atual.perfil == "Professor":
            alunos_supervisionados = (
                AlunoService.listar_por_professor(
                    db, usuario_atual.id_usuario
                )
            )

            if not any(
                item.id_aluno == aluno.id_aluno
                for item in alunos_supervisionados
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Você não possui permissão para consultar este aluno."
                )

            return aluno

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para consultar alunos."
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
    response_model=AlunoResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_aluno(
    dados: AlunoCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(check_role("Gestão"))
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


@router.patch(
    "/{id_aluno}",
    response_model=AlunoResponse,
    status_code=status.HTTP_200_OK
)
def atualizar_aluno(
    id_aluno: int,
    dados: AlunoUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(check_role("Gestão"))
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
