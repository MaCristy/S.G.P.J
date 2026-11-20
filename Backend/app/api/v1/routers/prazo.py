
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Dependências para acesso ao banco e identificação do usuário autenticado.
from app.api.deps import get_db, get_current_user
from app.models.usuario import Usuario

# Schemas utilizados na entrada e na resposta dos dados.
from app.schemas.prazo import (
    PrazoCreate,
    PrazoUpdate,
    PrazoResponse
)

# Serviço responsável pelas regras de negócio dos prazos.
from app.services.prazo_service import PrazoService


# Configuração das rotas de prazos.
router = APIRouter(
    prefix="/prazos",
    tags=["Prazos"]
)


# Lista os prazos disponíveis para o usuário autenticado.
@router.get("/", response_model=list[PrazoResponse])
def listar_prazos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return PrazoService.listar(db, usuario)

    except PermissionError as erro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )


# Lista os prazos vinculados a um caso jurídico específico.
@router.get("/caso/{id_caso}", response_model=list[PrazoResponse])
def listar_prazos_por_caso(
    id_caso: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return PrazoService.listar_por_caso(
            db, id_caso, usuario
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


# Lista os prazos atribuídos a um responsável específico.
@router.get(
    "/responsavel/{id_responsavel}",
    response_model=list[PrazoResponse]
)
def listar_prazos_por_responsavel(
    id_responsavel: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return PrazoService.listar_por_responsavel(
            db, id_responsavel, usuario
        )

    except PermissionError as erro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )


# Busca um prazo pelo seu identificador.
@router.get("/{id_prazo}", response_model=PrazoResponse)
def buscar_prazo(
    id_prazo: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return PrazoService.buscar_por_id(
            db, id_prazo, usuario
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


# Cadastra um novo prazo.
@router.post(
    "/",
    response_model=PrazoResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_prazo(
    dados: PrazoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return PrazoService.criar(
            db, dados, usuario
        )

    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )

    except PermissionError as erro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )


# Atualiza os dados de um prazo existente.
@router.patch("/{id_prazo}", response_model=PrazoResponse)
def atualizar_prazo(
    id_prazo: int,
    dados: PrazoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return PrazoService.atualizar(
            db, id_prazo, dados, usuario
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

    except PermissionError as erro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )
