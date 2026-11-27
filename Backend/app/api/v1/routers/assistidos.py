
"""
Rotas de gerenciamento dos assistidos do S.G.P.J.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.usuario import Usuario

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


# ============================================================
# 1. LISTAGEM DE ASSISTIDOS
# ============================================================

@router.get(
    "/",
    response_model=list[AssistidoResponse],
    status_code=status.HTTP_200_OK
)
def listar_assistidos(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        if usuario_atual.perfil == "Gestão":
            return AssistidoService.listar(db)

        if usuario_atual.perfil == "Aluno":
            return AssistidoService.listar_por_aluno(
                db,
                usuario_atual.id_usuario
            )

        if usuario_atual.perfil == "Professor":
            return AssistidoService.listar_por_professor(
                db,
                usuario_atual.id_usuario
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para listar assistidos."
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


# ============================================================
# 2. CONSULTA INDIVIDUAL DE ASSISTIDO
# ============================================================

@router.get(
    "/{id_assistido}",
    response_model=AssistidoResponse,
    status_code=status.HTTP_200_OK
)
def buscar_assistido(
    id_assistido: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        if usuario_atual.perfil == "Gestão":
            return AssistidoService.buscar_por_id(
                db,
                id_assistido
            )

        if usuario_atual.perfil == "Aluno":
            return AssistidoService.buscar_por_id_e_aluno(
                db,
                id_assistido,
                usuario_atual.id_usuario
            )

        if usuario_atual.perfil == "Professor":
            return AssistidoService.buscar_por_id_e_professor(
                db,
                id_assistido,
                usuario_atual.id_usuario
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para consultar assistidos."
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


# ============================================================
# 3. CADASTRO DE ASSISTIDO
# Gestão e Aluno podem cadastrar.
# ============================================================

@router.post(
    "/",
    response_model=AssistidoResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_assistido(
    dados: AssistidoCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        return AssistidoService.criar(
            db,
            dados,
            usuario_atual
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

    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(erro)
        )


# ============================================================
# 4. ATUALIZAÇÃO DE ASSISTIDO
# Gestão pode atualizar todos.
# Aluno pode atualizar os seus ou os vinculados aos seus casos.
# ============================================================

@router.patch(
    "/{id_assistido}",
    response_model=AssistidoResponse,
    status_code=status.HTTP_200_OK
)
def atualizar_assistido(
    id_assistido: int,
    dados: AssistidoUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        return AssistidoService.atualizar(
            db,
            id_assistido,
            dados,
            usuario_atual
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

    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(erro)
        )
