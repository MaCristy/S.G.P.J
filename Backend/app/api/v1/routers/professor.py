
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, check_role
from app.models.usuario import Usuario
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



@router.get(
    "/",
    response_model=list[ProfessorResponse],
    status_code=status.HTTP_200_OK
)
def listar_professores(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    if usuario_atual.perfil == "Gestão":
        return ProfessorService.listar(db)

    if usuario_atual.perfil == "Aluno":
        return ProfessorService.listar(db)

    if usuario_atual.perfil == "Professor":
        try:
            professor = ProfessorService.buscar_por_usuario(
                db, usuario_atual.id_usuario
            )
            return [professor]

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

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Você não possui permissão para listar professores."
    )




@router.get(
    "/{id_professor}",
    response_model=ProfessorResponse,
    status_code=status.HTTP_200_OK
)
def buscar_professor(
    id_professor: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        professor = ProfessorService.buscar_por_id(
            db, id_professor
        )

        if usuario_atual.perfil == "Gestão":
            return professor

        if usuario_atual.perfil == "Aluno":
            return professor

        if usuario_atual.perfil == "Professor":
            professor_atual = ProfessorService.buscar_por_usuario(
                db, usuario_atual.id_usuario
            )

            if professor.id_professor != professor_atual.id_professor:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Você só pode consultar seu próprio cadastro."
                )

            return professor

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para consultar professores."
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
    response_model=ProfessorResponse,
    status_code=status.HTTP_201_CREATED
)

def criar_professor(
    dados: ProfessorCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(check_role("Gestão"))
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
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(check_role("Gestão"))
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
