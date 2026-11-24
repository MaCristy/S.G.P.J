
from datetime import date, datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    model_validator
)


# Define os dados recebidos no pedido público de cadastro.
class SolicitacaoCadastroCreate(BaseModel):

    nome: str = Field(
        min_length=1,
        max_length=150
    )

    email_institucional: EmailStr = Field(
        max_length=150
    )

    senha: str = Field(
        min_length=8,
        max_length=128
    )

    confirmar_senha: str = Field(
        min_length=8,
        max_length=128
    )

    # Somente Aluno e Professor podem solicitar cadastro.
    perfil_solicitado: Literal["Aluno", "Professor"]

    # Dados específicos do aluno.
    matricula: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    curso: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    periodo: int | None = Field(
        default=None,
        gt=0
    )

    # Dados específicos do professor.
    identificacao_funcional: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    area_vinculo: str | None = Field(
        default=None,
        max_length=100
    )

    # Verifica a confirmação da senha e os campos correspondentes ao perfil.
    @model_validator(mode="after")
    def validar_solicitacao(self):

        # Confere se as duas senhas são iguais.
        if self.senha != self.confirmar_senha:
            raise ValueError(
                "A senha e a confirmação de senha não são iguais."
            )

        if self.perfil_solicitado == "Aluno":

            # Exige os dados acadêmicos necessários ao aluno.
            if not self.matricula or not self.curso or self.periodo is None:
                raise ValueError(
                    "Para solicitar cadastro como aluno, informe "
                    "matrícula, curso e período."
                )

            # Impede o envio de dados exclusivos de professor.
            if (
                self.identificacao_funcional is not None
                or self.area_vinculo is not None
            ):
                raise ValueError(
                    "Os campos funcionais não devem ser informados "
                    "em uma solicitação de aluno."
                )

        elif self.perfil_solicitado == "Professor":

            # Exige a identificação funcional do professor.
            if not self.identificacao_funcional:
                raise ValueError(
                    "A identificação funcional é obrigatória "
                    "para solicitar cadastro como professor."
                )

            # Impede o envio de dados exclusivos de aluno.
            if (
                self.matricula is not None
                or self.curso is not None
                or self.periodo is not None
            ):
                raise ValueError(
                    "Os campos acadêmicos de aluno não devem ser "
                    "informados em uma solicitação de professor."
                )

        return self


# Define os dados retornados pela API ao consultar uma solicitação.
class SolicitacaoCadastroResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id_solicitacao: int
    id_usuario: int
    perfil_solicitado: str

    matricula: str | None = None
    curso: str | None = None
    periodo: int | None = None

    identificacao_funcional: str | None = None
    area_vinculo: str | None = None

    situacao_academica: str | None = None
    data_vinculo: date | None = None

    status_solicitacao: str
    data_solicitacao: datetime
    data_analise: datetime | None = None

    id_gestor_analise: int | None = None
    observacao_analise: str | None = None


# Define os dados que a Gestão deve informar ao aprovar uma solicitação.
class SolicitacaoCadastroAprovacao(BaseModel):

    # Os dados acadêmicos serão obrigatórios somente para alunos.
    situacao_academica: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    data_vinculo: date | None = None

    # Permite registrar uma observação sobre a aprovação.
    observacao_analise: str | None = None


# Define os dados recebidos pela API ao rejeitar uma solicitação.
class SolicitacaoCadastroRejeicao(BaseModel):

    # Permite registrar o motivo ou uma observação da rejeição.
    observacao_analise: str | None = None
