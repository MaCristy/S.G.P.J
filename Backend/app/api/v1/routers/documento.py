
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.documento import (
    DocumentoCreate,
    DocumentoUpdate,
    DocumentoResponse
)
from app.services.documento_service import DocumentoService


router = APIRouter(
    prefix="/documentos",
    tags=["Documentos"]
)


@router.get("/", response_model=list[DocumentoResponse])
def listar_documentos(db: Session = Depends(get_db)):
    return DocumentoService.listar(db)


@router.get("/caso/{id_caso}", response_model=list[DocumentoResponse])
def listar_documentos_por_caso(
    id_caso: int,
    db: Session = Depends(get_db)
):
    try:
        return DocumentoService.listar_por_caso(db, id_caso)
    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )


@router.get(
    "/atendimento/{id_atendimento}",
    response_model=list[DocumentoResponse]
)
def listar_documentos_por_atendimento(
    id_atendimento: int,
    db: Session = Depends(get_db)
):
    try:
        return DocumentoService.listar_por_atendimento(
            db, id_atendimento
        )
    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )


@router.get("/{id_documento}", response_model=DocumentoResponse)
def buscar_documento(
    id_documento: int,
    db: Session = Depends(get_db)
):
    try:
        return DocumentoService.buscar_por_id(db, id_documento)
    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )


@router.post(
    "/",
    response_model=DocumentoResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_documento(
    dados: DocumentoCreate,
    db: Session = Depends(get_db)
):
    try:
        return DocumentoService.criar(db, dados)
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


@router.patch("/{id_documento}", response_model=DocumentoResponse)
def atualizar_documento(
    id_documento: int,
    dados: DocumentoUpdate,
    db: Session = Depends(get_db)
):
    try:
        return DocumentoService.atualizar(
            db, id_documento, dados
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
