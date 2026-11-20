
"""
Rotas de gerenciamento dos professores/orientadores do S.G.P.J.

Responsabilidades:
    - Listar os professores cadastrados.
    - Consultar professores individualmente.
    - Cadastrar novos professores.
    - Atualizar informações dos professores.
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
from app.schemas.professor import (
    ProfessorCreate,
    ProfessorUpdate,
    ProfessorResponse
)

# Serviço responsável pelas regras de negócio dos professores
from app.services.professor import ProfessorService


# ============================================================
# 1. CONFIGURAÇÃO DO ROTEADOR
# Define o prefixo e a identificação das rotas de professores.
# ============================================================

router = APIRouter(
    prefix="/professores",
    tags=["Professores/Orientadores"]
)


# ============================================================
# 2. LISTAGEM DE PROFESSORES
#
# Gestão: consulta todos os professores.
# Aluno: consulta todos os professores.
# Professor: consulta somente o próprio cadastro.
# ============================================================

@router.get(
    "/",
    response_model=list[ProfessorResponse],
    status_code=status.HTTP_200_OK
)
def listar_professores(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    # Gestão possui acesso à listagem completa
    if usuario_atual.perfil == "Gestão":
        return ProfessorService.listar(db)

    # Aluno pode consultar a lista de professores
    if usuario_atual.perfil == "Aluno":
        return ProfessorService.listar(db)

    # Professor visualiza somente seu próprio cadastro
    if usuario_atual.perfil == "Professor":
        try:
            professor = ProfessorService.buscar_por_usuario(
                db, usuario_atual.id_usuario
            )
            return [professor]

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

    # Bloqueia perfis sem permissão para consultar professores
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Você não possui permissão para listar professores."
    )


# ============================================================
# 3. CONSULTA INDIVIDUAL DE PROFESSOR
#
# Gestão: consulta qualquer professor.
# Aluno: consulta qualquer professor.
# Professor: consulta somente o próprio cadastro.
# ============================================================

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
        # Busca inicialmente o professor solicitado
        professor = ProfessorService.buscar_por_id(
            db, id_professor
        )

        # Gestão possui acesso a qualquer cadastro
        if usuario_atual.perfil == "Gestão":
            return professor

        # Aluno pode consultar qualquer professor
        if usuario_atual.perfil == "Aluno":
            return professor

        # Verifica se o professor autenticado está consultando
        # seu próprio cadastro
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

        # Bloqueia perfis sem permissão para consultar professores
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para consultar professores."
        )

    # Trata situações em que o professor não é encontrado
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
# 4. CADASTRO DE PROFESSOR
# Permite que somente a Gestão cadastre novos professores.
# ============================================================

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
        # Encaminha os dados recebidos ao serviço de professores
        return ProfessorService.criar(db, dados)

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
# 5. ATUALIZAÇÃO DE PROFESSOR
# Permite que somente a Gestão atualize os cadastros.
# ============================================================

@router.patch(
    "/{id_professor}",
    response_model=ProfessorResponse
)
def atualizar_professor(
    id_professor: int,
    dados: ProfessorUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(check_role("Gestão"))
):
    try:
        # Encaminha o identificador e os novos dados ao serviço
        return ProfessorService.atualizar(
            db, id_professor, dados
        )

    # Retorna erro quando o professor não é encontrado
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
