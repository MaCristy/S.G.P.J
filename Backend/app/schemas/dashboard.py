
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


# Define o período utilizado para consultar os indicadores.
class PeriodoDashboard(BaseModel):
    data_inicial: date
    data_final: date


# Define os indicadores numéricos apresentados no dashboard.
class IndicadoresDashboard(BaseModel):
    total_atendimentos: int = Field(ge=0)
    total_novos_casos: int = Field(ge=0)
    total_casos_ativos: int = Field(ge=0)
    total_casos_encerrados: int = Field(ge=0)
    total_atividades_pendentes: int = Field(ge=0)
    total_prazos_proximos: int = Field(ge=0)
    total_prazos_vencidos: int = Field(ge=0)


# Define os dados utilizados nas distribuições do dashboard.
class DistribuicaoDashboard(BaseModel):
    identificador: int | None = None
    nome: str
    quantidade: int = Field(ge=0)


# Define os itens que exigem atenção dos usuários.
class ItemAtencaoDashboard(BaseModel):
    tipo: Literal[
        "Prazo vencido",
        "Prazo próximo",
        "Atividade pendente"
    ]

    id_item: int
    descricao: str
    situacao: str
    data_referencia: date | None = None
    id_caso: int | None = None


# Define a estrutura completa da resposta do dashboard.
class DashboardResumoResponse(BaseModel):
    periodo: PeriodoDashboard
    indicadores: IndicadoresDashboard

    casos_por_situacao: list[DistribuicaoDashboard] = Field(
        default_factory=list
    )

    casos_por_aluno: list[DistribuicaoDashboard] = Field(
        default_factory=list
    )

    casos_por_professor: list[DistribuicaoDashboard] = Field(
        default_factory=list
    )

    atendimentos_por_aluno: list[DistribuicaoDashboard] = Field(
        default_factory=list
    )

    itens_atencao: list[ItemAtencaoDashboard] = Field(
        default_factory=list
    )


# ============================================================
# DADOS EXIBIDOS NA VISÃO GERAL DO ALUNO E DO PROFESSOR
# ============================================================

class AtividadeDashboardItem(BaseModel):
    id_atividade: int
    titulo: str
    codigo_caso: str
    situacao: str
    data_prevista: date | None = None


class PrazoDashboardItem(BaseModel):
    id_prazo: int
    descricao: str
    codigo_caso: str
    situacao: str
    data_limite: date


class DashboardAlunoResponse(BaseModel):
    total_casos: int
    total_atividades_pendentes: int
    total_prazos_proximos: int
    total_atividades_concluidas: int
    atividades_recentes: list[AtividadeDashboardItem] = Field(
        default_factory=list
    )
    prazos_proximos: list[PrazoDashboardItem] = Field(
        default_factory=list
    )


class DashboardProfessorResponse(BaseModel):
    total_casos: int
    total_alunos: int
    total_atividades: int
    total_prazos_proximos: int
    atividades_recentes: list[AtividadeDashboardItem] = Field(
        default_factory=list
    )
    prazos_proximos: list[PrazoDashboardItem] = Field(
        default_factory=list
    )

