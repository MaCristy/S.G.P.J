
"""
Rotas de gerenciamento dos alunos/estagiários do S.G.P.J.

Responsabilidades:
    - Listar os alunos cadastrados.
    - Consultar alunos individualmente.
    - Cadastrar novos alunos.
    - Atualizar informações dos alunos.
    - Restringir consultas conforme o perfil do usuário.
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
from app.schemas.aluno import (
    AlunoCreate,
    AlunoUpdate,
    AlunoResponse
)

# Serviço responsável pelas regras de negócio dos alunos
from app.services.aluno import AlunoService


# ============================================================
# 1. CONFIGURAÇÃO DO ROTEADOR
# Define o prefixo e a identificação das rotas de alunos.
# ============================================================

router = APIRouter(
    prefix="/alunos",
    tags=["Alunos/Estagiários"]
)


# ============================================================
# 2. LISTAGEM DE ALUNOS
#
# Gestão: consulta todos os alunos.
# Professor: consulta os alunos sob sua supervisão.
# Aluno: consulta somente o próprio cadastro.
# ============================================================

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
        # Gestão possui acesso à listagem completa
        if usuario_atual.perfil == "Gestão":
            return AlunoService.listar(db)

        # Professor visualiza somente os alunos supervisionados
        if usuario_atual.perfil == "Professor":
            return AlunoService.listar_por_professor(
                db, usuario_atual.id_usuario
            )

        # Aluno visualiza somente seu próprio cadastro
        if usuario_atual.perfil == "Aluno":
            aluno = AlunoService.buscar_por_usuario(
                db, usuario_atual.id_usuario
            )
            return [aluno]

        # Bloqueia perfis sem permissão para consultar alunos
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para listar alunos."
        )

    # Trata situações em que o cadastro não é encontrado
    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )

    # Trata restrições de acesso identificadas pelo serviço
    except PermissionError as erro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )


# ============================================================
# 3. CONSULTA INDIVIDUAL DE ALUNO
#
# Gestão: consulta qualquer aluno.
# Professor: consulta alunos supervisionados.
# Aluno: consulta somente o próprio cadastro.
# ============================================================

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
        # Busca inicialmente o aluno solicitado
        aluno = AlunoService.buscar_por_id(db, id_aluno)

        # Gestão possui acesso a qualquer cadastro
        if usuario_atual.perfil == "Gestão":
            return aluno

        # Verifica se o aluno autenticado está consultando
        # seu próprio cadastro
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

        # Verifica se o professor supervisiona o aluno solicitado
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

        # Bloqueia perfis sem permissão para consultar alunos
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para consultar alunos."
        )

    # Trata situações em que o aluno não é encontrado
    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )

    # Trata restrições de acesso identificadas pelo serviço
    except PermissionError as erro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )


# ============================================================
# 4. CADASTRO DE ALUNO
# Permite que somente a Gestão cadastre novos alunos.
# ============================================================

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
        # Encaminha os dados recebidos ao serviço de alunos
        return AlunoService.criar(db, dados)

    # Trata referências não encontradas durante o cadastro
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


# ============================================================
# 5. ATUALIZAÇÃO DE ALUNO
# Permite que somente a Gestão atualize os cadastros.
# ============================================================

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
        # Encaminha o identificador e os novos dados ao serviço
        return AlunoService.atualizar(db, id_aluno, dados)

    # Retorna erro quando o aluno não é encontrado
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
