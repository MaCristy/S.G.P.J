"""
Rotas para solicitação pública e análise de cadastros do S.G.P.J.

Responsabilidades:
    - Receber solicitações públicas de Alunos e Professores.
    - Permitir que a Gestão consulte as solicitações.
    - Permitir que a Gestão aprove ou rejeite solicitações.
"""

# Componentes do FastAPI para criação de rotas, dependências e respostas HTTP.
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Dependências de banco de dados e controle de acesso.
from app.api.deps import get_db, check_role

# Modelo do usuário autenticado.
from app.models.usuario import Usuario

# Schemas para entrada e saída dos dados das solicitações.
from app.schemas.solicitacao_cadastro import (
    SolicitacaoCadastroCreate,
    SolicitacaoCadastroResponse,
    SolicitacaoCadastroAprovacao,
    SolicitacaoCadastroRejeicao
)

# Serviço responsável pelas regras de negócio das solicitações.
from app.services.solicitacao_cadastro import SolicitacaoCadastroService


# Define o prefixo e a identificação das rotas de solicitações.
router = APIRouter(
    prefix="/solicitacoes-cadastro",
    tags=["Solicitações de Cadastro"]
)


# Recebe uma solicitação pública de cadastro de Aluno ou Professor.
@router.post(
    "/",
    response_model=SolicitacaoCadastroResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_solicitacao_cadastro(
    dados: SolicitacaoCadastroCreate,
    db: Session = Depends(get_db)
):
    try:
        # Encaminha os dados ao serviço, que cria a conta como Pendente.
        return SolicitacaoCadastroService.criar(db, dados)

    except ValueError as erro:
        # Informa quando os dados conflitam com um cadastro existente.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )


# Lista as solicitações para consulta exclusiva da Gestão.
@router.get(
    "/",
    response_model=list[SolicitacaoCadastroResponse],
    status_code=status.HTTP_200_OK
)
def listar_solicitacoes_cadastro(
    status_solicitacao: Literal["Pendente", "Aprovada", "Rejeitada"] | None = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(check_role("Gestão"))
):
    # Encaminha o filtro opcional ao serviço de solicitações.
    return SolicitacaoCadastroService.listar(
        db, status_solicitacao
    )


# Consulta uma solicitação específica, disponível somente para a Gestão.
@router.get(
    "/{id_solicitacao}",
    response_model=SolicitacaoCadastroResponse,
    status_code=status.HTTP_200_OK
)
def buscar_solicitacao_cadastro(
    id_solicitacao: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(check_role("Gestão"))
):
    try:
        # Busca a solicitação pelo identificador informado.
        return SolicitacaoCadastroService.buscar_por_id(
            db, id_solicitacao
        )

    except LookupError as erro:
        # Retorna 404 quando a solicitação não existe.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )


# Aprova uma solicitação e cria o cadastro definitivo correspondente.
@router.patch(
    "/{id_solicitacao}/aprovar",
    response_model=SolicitacaoCadastroResponse,
    status_code=status.HTTP_200_OK
)
def aprovar_solicitacao_cadastro(
    id_solicitacao: int,
    dados: SolicitacaoCadastroAprovacao,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(check_role("Gestão"))
):
    try:
        # Usa o ID do gestor autenticado para registrar quem analisou.
        return SolicitacaoCadastroService.aprovar(
            db=db,
            id_solicitacao=id_solicitacao,
            id_gestor=usuario_atual.id_usuario,
            dados=dados
        )

    except LookupError as erro:
        # Retorna 404 quando a solicitação ou usuário não é encontrado.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )

    except PermissionError as erro:
        # Bloqueia a operação se o gestor não puder realizar a análise.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )

    except ValueError as erro:
        # Informa quando a solicitação não pode ser aprovada.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )


# Rejeita uma solicitação e mantém a conta do solicitante bloqueada.
@router.patch(
    "/{id_solicitacao}/rejeitar",
    response_model=SolicitacaoCadastroResponse,
    status_code=status.HTTP_200_OK
)
def rejeitar_solicitacao_cadastro(
    id_solicitacao: int,
    dados: SolicitacaoCadastroRejeicao,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(check_role("Gestão"))
):
    try:
        # Registra a rejeição e identifica o gestor responsável.
        return SolicitacaoCadastroService.rejeitar(
            db=db,
            id_solicitacao=id_solicitacao,
            id_gestor=usuario_atual.id_usuario,
            dados=dados
        )

    except LookupError as erro:
        # Retorna 404 quando a solicitação ou usuário não é encontrado.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )

    except PermissionError as erro:
        # Bloqueia a operação se o gestor não puder realizar a análise.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )

    except ValueError as erro:
        # Informa quando a solicitação não pode ser rejeitada.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )
