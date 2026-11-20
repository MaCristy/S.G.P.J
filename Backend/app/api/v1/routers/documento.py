
from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

# Dependências para acesso ao banco e identificação do usuário autenticado.
from app.api.deps import get_db, get_current_user

# Configurações do armazenamento de documentos.
from app.config.settings import settings

from app.models.usuario import Usuario

# Schemas utilizados na entrada e na resposta dos dados.
from app.schemas.documento import (
    DocumentoCreate,
    DocumentoUpdate,
    DocumentoResponse
)

# Serviço responsável pelas regras de negócio dos documentos.
from app.services.documento_service import DocumentoService


# Configuração das rotas de documentos.
router = APIRouter(
    prefix="/documentos",
    tags=["Documentos"]
)


# Lista os documentos disponíveis para o usuário autenticado.
@router.get("/", response_model=list[DocumentoResponse])
def listar_documentos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return DocumentoService.listar(db, usuario)

    except PermissionError as erro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )


# Lista os documentos vinculados a um caso jurídico.
@router.get("/caso/{id_caso}", response_model=list[DocumentoResponse])
def listar_documentos_por_caso(
    id_caso: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return DocumentoService.listar_por_caso(
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


# Lista os documentos vinculados a um atendimento.
@router.get(
    "/atendimento/{id_atendimento}",
    response_model=list[DocumentoResponse]
)
def listar_documentos_por_atendimento(
    id_atendimento: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return DocumentoService.listar_por_atendimento(
            db, id_atendimento, usuario
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


# Recebe, valida e armazena um arquivo PDF.
@router.post(
    "/upload",
    response_model=DocumentoResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_documento(
    arquivo: UploadFile = File(...),
    id_caso: int | None = Form(None),
    id_atendimento: int | None = Form(None, ge=1),
    classificacao_acesso: str | None = Form(None),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    # Valida o nome original do arquivo.
    nome_original = Path(arquivo.filename or "").name.strip()

    if not nome_original:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo precisa ter um nome válido."
        )

    # Permite somente arquivos com extensão PDF.
    if Path(nome_original).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas arquivos PDF são permitidos."
        )

    # Verifica o tipo de conteúdo informado no envio.
    if arquivo.content_type not in (
        None,
        "application/pdf",
        "application/octet-stream"
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O tipo de arquivo enviado não é permitido."
        )

    # Lê o arquivo respeitando o limite máximo configurado.
    limite_bytes = settings.DOCUMENTOS_MAX_SIZE_MB * 1024 * 1024

    conteudo = await arquivo.read(limite_bytes + 1)

    if not conteudo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo enviado está vazio."
        )

    if len(conteudo) > limite_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"O arquivo ultrapassa o limite de "
                f"{settings.DOCUMENTOS_MAX_SIZE_MB} MB."
            )
        )

    # Confirma a assinatura inicial de um arquivo PDF.
    if not conteudo.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O conteúdo enviado não corresponde a um PDF válido."
        )

    # Gera um nome interno único para o armazenamento.
    nome_arquivo = f"{uuid4().hex}.pdf"

    diretorio = settings.DOCUMENTOS_DIR.resolve()
    caminho_arquivo = diretorio / nome_arquivo

    # Prepara os metadados que serão registrados no banco.
    dados = DocumentoCreate(
        id_caso=id_caso,
        id_atendimento=id_atendimento,
        nome=nome_original[:255],
        tipo="application/pdf",
        caminho_armazenamento=nome_arquivo,
        id_usuario_inclusao=usuario.id_usuario,
        classificacao_acesso=classificacao_acesso
    )

    try:
        # Cria a pasta privada e grava o arquivo.
        diretorio.mkdir(parents=True, exist_ok=True)
        caminho_arquivo.write_bytes(conteudo)

        # Registra os dados do documento no banco.
        documento = DocumentoService.criar(
            db,
            dados,
            usuario
        )

        return documento

    except PermissionError as erro:
        caminho_arquivo.unlink(missing_ok=True)

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )

    except LookupError as erro:
        caminho_arquivo.unlink(missing_ok=True)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )

    except ValueError as erro:
        caminho_arquivo.unlink(missing_ok=True)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )

    except Exception:
        # Remove o arquivo físico se ocorrer uma falha no processamento.
        caminho_arquivo.unlink(missing_ok=True)
        raise

    finally:
        # Fecha o arquivo recebido após o processamento.
        await arquivo.close()


# Disponibiliza o arquivo físico após verificar as permissões.
@router.get("/{id_documento}/arquivo")
def baixar_arquivo_documento(
    id_documento: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        documento = DocumentoService.buscar_por_id(
            db, id_documento, usuario
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

    diretorio = settings.DOCUMENTOS_DIR.resolve()

    caminho_arquivo = (
        diretorio / documento.caminho_armazenamento
    ).resolve()

    # Impede que o acesso ultrapasse os limites da pasta autorizada.
    if (
        caminho_arquivo == diretorio
        or diretorio not in caminho_arquivo.parents
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado."
        )

    # Verifica se o arquivo físico realmente existe.
    if not caminho_arquivo.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="O arquivo físico deste documento não foi encontrado."
        )

    # Retorna o PDF para download.
    return FileResponse(
        path=caminho_arquivo,
        media_type="application/pdf",
        filename=Path(documento.nome).name
    )


# Busca os metadados de um documento pelo identificador.
@router.get("/{id_documento}", response_model=DocumentoResponse)
def buscar_documento(
    id_documento: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return DocumentoService.buscar_por_id(
            db, id_documento, usuario
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


# Cadastra os metadados de um documento.
@router.post(
    "/",
    response_model=DocumentoResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_documento(
    dados: DocumentoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return DocumentoService.criar(
            db, dados, usuario
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


# Atualiza os metadados de um documento existente.
@router.patch(
    "/{id_documento}",
    response_model=DocumentoResponse
)
def atualizar_documento(
    id_documento: int,
    dados: DocumentoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return DocumentoService.atualizar(
            db, id_documento, dados, usuario
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
