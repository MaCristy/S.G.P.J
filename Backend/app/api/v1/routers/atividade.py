
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Dependências para acesso ao banco e identificação do usuário autenticado.
from app.api.deps import get_db, get_current_user
from app.models.usuario import Usuario

# Schemas utilizados na entrada e na resposta dos dados.
from app.schemas.atividade import (
    AtividadeCreate,
    AtividadeUpdate,
    AtividadeResponse
)

# Serviço responsável pelas regras de negócio das atividades.
from app.services.atividade import AtividadeService


# Configuração das rotas de atividades.
router = APIRouter(
    prefix="/atividades",
    tags=["Atividades"]
)


# Lista as atividades disponíveis para o usuário autenticado.
@router.get("/", response_model=list[AtividadeResponse])
def listar_atividades(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return AtividadeService.listar(db, usuario)

    except PermissionError as erro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )


# Lista as atividades vinculadas a um caso jurídico específico.
@router.get("/caso/{id_caso}", response_model=list[AtividadeResponse])
def listar_atividades_por_caso(
    id_caso: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return AtividadeService.listar_por_caso(
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


# Lista as atividades atribuídas a um responsável específico.
@router.get(
    "/responsavel/{id_responsavel}",
    response_model=list[AtividadeResponse]
)
def listar_atividades_por_responsavel(
    id_responsavel: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return AtividadeService.listar_por_responsavel(
            db, id_responsavel, usuario
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


# Busca uma atividade pelo seu identificador.
@router.get("/{id_atividade}", response_model=AtividadeResponse)
def buscar_atividade(
    id_atividade: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return AtividadeService.buscar_por_id(
            db, id_atividade, usuario
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


# Cadastra uma nova atividade.
@router.post(
    "/",
    response_model=AtividadeResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_atividade(
    dados: AtividadeCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return AtividadeService.criar(
            db, dados, usuario
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )


# Atualiza os dados de uma atividade existente.
@router.patch(
    "/{id_atividade}",
    response_model=AtividadeResponse
)
def atualizar_atividade(
    id_atividade: int,
    dados: AtividadeUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return AtividadeService.atualizar(
            db, id_atividade, dados, usuario
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )
