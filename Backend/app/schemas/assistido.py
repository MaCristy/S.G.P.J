
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AssistidoBase(BaseModel):
    """Campos compartilhados do assistido."""

    nome_completo: str = Field(
        min_length=1,
        max_length=200
    )

    identificador_cadastral: str = Field(
        min_length=1,
        max_length=50
    )

    contato: str = Field(
        min_length=1,
        max_length=100
    )

    endereco: str | None = None
    observacoes_administrativas: str | None = None


class AssistidoCreate(AssistidoBase):
    """Dados necessários para cadastrar um assistido."""

    situacao: str = Field(
        default="Ativo",
        max_length=30
    )


class AssistidoUpdate(BaseModel):
    """Dados permitidos para atualizar um assistido."""

    nome_completo: str | None = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    identificador_cadastral: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    contato: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    endereco: str | None = None
    observacoes_administrativas: str | None = None

    situacao: str | None = Field(
        default=None,
        max_length=30
    )


class AssistidoResponse(AssistidoBase):
    """Formato dos dados retornados pela API."""

    model_config = ConfigDict(from_attributes=True)

    id_assistido: int
    data_cadastro: datetime
    situacao: str
