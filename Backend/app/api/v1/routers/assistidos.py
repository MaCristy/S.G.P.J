
"""
Rotas de gerenciamento dos assistidos do S.G.P.J.

Responsabilidades:
    - Listar e consultar assistidos.
    - Cadastrar novos assistidos.
    - Atualizar informações dos assistidos.
    - Restringir operações conforme o perfil do usuário.
"""

# Componentes do FastAPI para criação de rotas, dependências e respostas HTTP
from fastapi import APIRouter, Depends, HTTPException, status

# Sessão de conexão com o banco de dados
from sqlalchemy.orm import Session

# Dependências de autenticação, conexão e controle de permissões
from app.api.deps import get_db, get_current_user, check_role

# Modelo do usuário autenticado
from app.models.usuario import Usuario

# Schemas para validação dos dados de entrada e saída
from app.schemas.assistido import (
    AssistidoCreate,
    AssistidoUpdate,
    AssistidoResponse
)

# Serviço responsável pelas regras de negócio dos assistidos
from app.services.assistido import AssistidoService


# ============================================================
# 1. CONFIGURAÇÃO DO ROTEADOR
# Define o prefixo e a identificação das rotas de assistidos.
# ============================================================

router = APIRouter(
    prefix="/assistidos",
    tags=["Assistidos"]
)


# ============================================================
# 2. LISTAGEM DE ASSISTIDOS
# Retorna os assistidos conforme o perfil e as permissões do usuário.
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
        # Gestão pode consultar todos os assistidos
        if usuario_atual.perfil == "Gestão":
            return AssistidoService.listar(db)

        # Aluno consulta os assistidos relacionados aos seus casos
        if usuario_atual.perfil == "Aluno":
            return AssistidoService.listar_por_aluno(
                db,
                usuario_atual.id_usuario
            )

        # Professor consulta os assistidos dos casos supervisionados
        if usuario_atual.perfil == "Professor":
            return AssistidoService.listar_por_professor(
                db,
                usuario_atual.id_usuario
            )

        # Bloqueia perfis sem autorização para listar assistidos
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para listar assistidos."
        )

    # Trata situações em que o registro não é encontrado
    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )

    # Trata tentativas de acesso sem permissão
    except PermissionError as erro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )


# ============================================================
# 3. CONSULTA DE ASSISTIDO
# Busca um assistido pelo identificador, respeitando as permissões.
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
        # Gestão pode consultar qualquer assistido
        if usuario_atual.perfil == "Gestão":
            return AssistidoService.buscar_por_id(
                db, id_assistido
            )

        # Aluno só pode consultar assistidos relacionados aos seus casos
        if usuario_atual.perfil == "Aluno":
            return AssistidoService.buscar_por_id_e_aluno(
                db,
                id_assistido,
                usuario_atual.id_usuario
            )

        # Professor só pode consultar assistidos dos casos supervisionados
        if usuario_atual.perfil == "Professor":
            return AssistidoService.buscar_por_id_e_professor(
                db,
                id_assistido,
                usuario_atual.id_usuario
            )

        # Bloqueia perfis sem autorização para consultar assistidos
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para consultar assistidos."
        )

    # Retorna erro quando o assistido não é encontrado ou não está acessível
    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )

    # Trata tentativas de acesso sem permissão
    except PermissionError as erro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )


# ============================================================
# 4. CADASTRO DE ASSISTIDO
# Permite que usuários da Gestão cadastrem novos assistidos.
# ============================================================

@router.post(
    "/",
    response_model=AssistidoResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_assistido(
    dados: AssistidoCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(check_role("Gestão"))
):
    try:
        # Encaminha os dados ao serviço para realizar o cadastro
        return AssistidoService.criar(db, dados)

    # Trata conflitos ou inconsistências nos dados enviados
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(erro)
        )


# ============================================================
# 5. ATUALIZAÇÃO DE ASSISTIDO
# Permite que a Gestão atualize os dados de um assistido existente.
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
    usuario_atual: Usuario = Depends(check_role("Gestão"))
):
    try:
        # Encaminha o identificador e os novos dados ao serviço
        return AssistidoService.atualizar(
            db,
            id_assistido,
            dados
        )

    # Trata situações em que o assistido não existe
    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )

    # Trata conflitos ou inconsistências na atualização
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(erro)
        )
