
"""
Rotas de gerenciamento dos atendimentos do S.G.P.J.

Responsabilidades:
    - Listar atendimentos conforme o perfil do usuário.
    - Consultar atendimentos por assistido.
    - Buscar um atendimento específico.
    - Registrar novos atendimentos.
"""

# Componentes do FastAPI para criação de rotas, dependências e respostas HTTP
from fastapi import APIRouter, Depends, HTTPException, status

# Sessão de conexão com o banco de dados
from sqlalchemy.orm import Session

# Dependências de conexão e autenticação
from app.api.deps import get_db, get_current_user

# Schemas para validação dos dados de entrada e saída
from app.schemas.atendimento import (
    AtendimentoCreate,
    AtendimentoResponse
)

# Serviço responsável pelas regras de negócio dos atendimentos
from app.services.atendimento import AtendimentoService

# Modelo do usuário autenticado
from app.models.usuario import Usuario


# ============================================================
# 1. CONFIGURAÇÃO DO ROTEADOR
# Define o prefixo e a identificação das rotas de atendimentos.
# ============================================================

router = APIRouter(
    prefix="/atendimentos",
    tags=["Atendimentos"]
)


# ============================================================
# 2. LISTAGEM DE ATENDIMENTOS
# Retorna os atendimentos conforme o perfil e as permissões.
# ============================================================

@router.get(
    "/",
    response_model=list[AtendimentoResponse],
    status_code=status.HTTP_200_OK
)
def listar_atendimentos(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        # Gestão pode consultar todos os atendimentos
        if usuario_atual.perfil == "Gestão":
            return AtendimentoService.listar(db)

        # Aluno consulta os atendimentos relacionados aos seus casos
        if usuario_atual.perfil == "Aluno":
            return AtendimentoService.listar_por_aluno(
                db,
                usuario_atual.id_usuario
            )

        # Professor consulta os atendimentos dos casos supervisionados
        if usuario_atual.perfil == "Professor":
            return AtendimentoService.listar_por_professor(
                db,
                usuario_atual.id_usuario
            )

        # Bloqueia perfis sem autorização para listar atendimentos
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para listar atendimentos."
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
# 3. LISTAGEM DE ATENDIMENTOS POR ASSISTIDO
# Retorna os atendimentos vinculados a um assistido específico.
# ============================================================

@router.get(
    "/assistido/{id_assistido}",
    response_model=list[AtendimentoResponse],
    status_code=status.HTTP_200_OK
)
def listar_atendimentos_por_assistido(
    id_assistido: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        # Gestão pode consultar os atendimentos de qualquer assistido
        if usuario_atual.perfil == "Gestão":
            return AtendimentoService.listar_por_assistido(
                db, id_assistido
            )

        # Aluno consulta atendimentos de assistidos relacionados aos seus casos
        if usuario_atual.perfil == "Aluno":
            return AtendimentoService.listar_por_assistido_e_aluno(
                db,
                id_assistido,
                usuario_atual.id_usuario
            )

        # Professor consulta atendimentos de assistidos dos casos supervisionados
        if usuario_atual.perfil == "Professor":
            return AtendimentoService.listar_por_assistido_e_professor(
                db,
                id_assistido,
                usuario_atual.id_usuario
            )

        # Bloqueia perfis sem autorização para consultar atendimentos
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para consultar atendimentos."
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
# 4. CONSULTA DE ATENDIMENTO
# Busca um atendimento específico pelo seu identificador.
# ============================================================

@router.get(
    "/{id_atendimento}",
    response_model=AtendimentoResponse,
    status_code=status.HTTP_200_OK
)
def buscar_atendimento(
    id_atendimento: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        # Gestão pode consultar qualquer atendimento
        if usuario_atual.perfil == "Gestão":
            return AtendimentoService.buscar_por_id(
                db, id_atendimento
            )

        # Aluno só pode consultar atendimentos relacionados aos seus casos
        if usuario_atual.perfil == "Aluno":
            return AtendimentoService.buscar_por_id_e_aluno(
                db,
                id_atendimento,
                usuario_atual.id_usuario
            )

        # Professor só pode consultar atendimentos dos casos supervisionados
        if usuario_atual.perfil == "Professor":
            return AtendimentoService.buscar_por_id_e_professor(
                db,
                id_atendimento,
                usuario_atual.id_usuario
            )

        # Bloqueia perfis sem autorização para consultar o atendimento
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para consultar este atendimento."
        )

    # Trata situações em que o atendimento não é encontrado
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
# 5. CADASTRO DE ATENDIMENTO
# Registra um atendimento e identifica o usuário responsável
# pelo cadastro para aplicação das regras de negócio.
# ============================================================

@router.post(
    "/",
    response_model=AtendimentoResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_atendimento(
    dados: AtendimentoCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        # Encaminha os dados, o identificador e o perfil do usuário ao serviço
        return AtendimentoService.criar(
            db,
            dados,
            usuario_atual.id_usuario,
            usuario_atual.perfil
        )

    # Trata referências a registros inexistentes
    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )

    # Trata dados inválidos ou inconsistências no cadastro
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )

    # Trata tentativas de cadastro sem permissão
    except PermissionError as erro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )
