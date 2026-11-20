
"""
Rotas de gerenciamento dos usuários do S.G.P.J.

Responsabilidades:
    - Listar os usuários cadastrados.
    - Consultar usuários individualmente.
    - Cadastrar novos usuários.
    - Atualizar informações dos usuários.
    - Controlar o acesso conforme o perfil autenticado.
"""

# Componentes do FastAPI para criação de rotas, dependências e respostas HTTP
from fastapi import APIRouter, Depends, HTTPException, status

# Sessão de conexão com o banco de dados
from sqlalchemy.orm import Session

# Dependências de conexão, autenticação e controle de permissões
from app.api.deps import get_db, get_current_user, check_role

# Modelo do usuário autenticado
from app.models.usuario import Usuario

# Schemas para validação dos dados de entrada e saída
from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse
)

# Serviço responsável pelas regras de negócio dos usuários
from app.services.usuario import UsuarioService


# ============================================================
# 1. CONFIGURAÇÃO DO ROTEADOR
# Define o prefixo e a identificação das rotas de usuários.
# ============================================================

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)


# ============================================================
# 2. LISTAGEM DE USUÁRIOS
# Permite que somente a Gestão consulte todos os usuários.
# ============================================================

@router.get(
    "/",
    response_model=list[UsuarioResponse],
    status_code=status.HTTP_200_OK
)
def listar_usuarios(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(check_role("Gestão"))
):
    # Encaminha a consulta ao serviço de usuários
    return UsuarioService.listar(db)


# ============================================================
# 3. CONSULTA DE USUÁRIO
# Busca um usuário pelo identificador.
#
# Gestão pode consultar qualquer cadastro.
# Aluno e Professor só podem consultar o próprio cadastro.
# ============================================================

@router.get(
    "/{id_usuario}",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK
)
def buscar_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    # Impede que Aluno e Professor consultem cadastros de terceiros
    if (
        usuario_atual.perfil != "Gestão"
        and usuario_atual.id_usuario != id_usuario
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para consultar este usuário."
        )

    try:
        # Busca o usuário solicitado
        return UsuarioService.buscar_por_id(db, id_usuario)

    # Retorna erro quando o usuário não é encontrado
    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )


# ============================================================
# 4. CADASTRO DE USUÁRIO
# Permite que somente a Gestão cadastre novos usuários.
# ============================================================

@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_usuario(
    dados: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(check_role("Gestão"))
):
    try:
        # Encaminha os dados recebidos ao serviço para cadastro
        return UsuarioService.criar(db, dados)

    # Trata dados inválidos ou conflitos no cadastro
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )


# ============================================================
# 5. ATUALIZAÇÃO DE USUÁRIO
# Permite que somente a Gestão atualize os cadastros existentes.
# ============================================================

@router.patch(
    "/{id_usuario}",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK
)
def atualizar_usuario(
    id_usuario: int,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(check_role("Gestão"))
):
    try:
        # Encaminha o identificador e os novos dados ao serviço
        return UsuarioService.atualizar(
            db, id_usuario, dados
        )

    # Retorna erro quando o usuário não é encontrado
    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )

    # Trata dados inválidos ou inconsistências na atualização
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )
