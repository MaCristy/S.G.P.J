
from datetime import date

from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import DashboardRepository

from app.schemas.dashboard import (
    PeriodoDashboard,
    IndicadoresDashboard,
    DistribuicaoDashboard,
    ItemAtencaoDashboard,
    DashboardResumoResponse
)


class DashboardService:

    @staticmethod
    def obter_resumo(
        db: Session,
        data_inicial: date | None = None,
        data_final: date | None = None
    ) -> DashboardResumoResponse:

        hoje = date.today()

        # Define o período padrão: primeiro dia do mês até hoje.
        if data_inicial is None:
            data_inicial = hoje.replace(day=1)

        if data_final is None:
            data_final = hoje

        # Verifica se o período informado é válido.
        if data_inicial > data_final:
            raise ValueError(
                "A data inicial não pode ser posterior à data final."
            )

        # Obtém os indicadores gerais.
        indicadores = IndicadoresDashboard(
            total_atendimentos=(
                DashboardRepository.obter_total_atendimentos(
                    db,
                    data_inicial,
                    data_final
                )
            ),

            total_novos_casos=(
                DashboardRepository.obter_total_novos_casos(
                    db,
                    data_inicial,
                    data_final
                )
            ),

            total_casos_ativos=(
                DashboardRepository.obter_total_casos_ativos(db)
            ),

            total_casos_encerrados=(
                DashboardRepository.obter_total_casos_encerrados(
                    db,
                    data_inicial,
                    data_final
                )
            ),

            total_atividades_pendentes=(
                DashboardRepository.obter_total_atividades_pendentes(db)
            ),

            total_prazos_proximos=(
                DashboardRepository.obter_total_prazos_proximos(db)
            ),

            total_prazos_vencidos=(
                DashboardRepository.obter_total_prazos_vencidos(db)
            )
        )

        # Distribuição de casos por situação.
        casos_por_situacao = [
            DistribuicaoDashboard(**item)
            for item in DashboardRepository.obter_casos_por_situacao(db)
        ]

        # Distribuição de casos por aluno.
        casos_por_aluno = [
            DistribuicaoDashboard(**item)
            for item in DashboardRepository.obter_casos_por_aluno(db)
        ]

        # Distribuição de casos por professor.
        casos_por_professor = [
            DistribuicaoDashboard(**item)
            for item in DashboardRepository.obter_casos_por_professor(db)
        ]

        # Distribuição de atendimentos por aluno.
        atendimentos_por_aluno = [
            DistribuicaoDashboard(**item)
            for item in DashboardRepository.obter_atendimentos_por_aluno(
                db,
                data_inicial,
                data_final
            )
        ]


        # Reúne os itens que precisam de atenção.
        itens_atencao = []

        itens_atencao.extend(
            DashboardRepository.obter_prazos_vencidos(db)
        )

        itens_atencao.extend(
            DashboardRepository.obter_prazos_proximos(db)
        )

        itens_atencao.extend(
            DashboardRepository.obter_atividades_pendentes(db)
        )

        # Converte os resultados para o schema de resposta.
        itens_atencao = [
            ItemAtencaoDashboard(**item)
            for item in itens_atencao
        ]

        # Organiza e retorna o resumo completo.
        return DashboardResumoResponse(
            periodo=PeriodoDashboard(
                data_inicial=data_inicial,
                data_final=data_final
            ),

            indicadores=indicadores,

            casos_por_situacao=casos_por_situacao,

            casos_por_aluno=casos_por_aluno,

            casos_por_professor=casos_por_professor,

            atendimentos_por_aluno=atendimentos_por_aluno,

            itens_atencao=itens_atencao
        )
