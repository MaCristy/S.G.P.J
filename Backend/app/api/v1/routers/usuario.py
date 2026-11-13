
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.services.usuario import UsuarioService


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)


@router.get(
    "/",
    response_model=list[UsuarioResponse],
    status_code=status.HTTP_200_OK
)
def listar_usuarios(db: Session = Depends(get_db)):
    return UsuarioService.listar(db)


@router.get(
    "/{id_usuario}",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK
)
def buscar_usuario(
    id_usuario: int,
    db: Session = Depends(get_db)
):
    try:
        return UsuarioService.buscar_por_id(db, id_usuario)

    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )


@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_usuario(
    dados: UsuarioCreate,
    db: Session = Depends(get_db)
):
    try:
        return UsuarioService.criar(db, dados)

    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )
