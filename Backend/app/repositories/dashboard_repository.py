
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.atendimento import Atendimento
from app.models.caso_juridico import CasoJuridico
from app.models.atividade import Atividade
from app.models.prazo import Prazo
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.usuario import Usuario


class DashboardRepository:
    """
    Centraliza as consultas utilizadas para gerar os indicadores
    e as informações exibidas no painel de gestão.
    """

    @staticmethod
    def _contar(query) -> int:
        # Executa a consulta de contagem e retorna zero caso não haja resultados.
        return query.scalar() or 0

    @staticmethod
    def obter_total_atendimentos(
        db: Session,
        data_inicial: date,
        data_final: date
    ) -> int:
        # Conta os atendimentos registrados dentro do período informado.
        return DashboardRepository._contar(
            db.query(func.count(Atendimento.id_atendimento))
            .filter(
                func.date(Atendimento.data_hora) >= data_inicial,
                func.date(Atendimento.data_hora) <= data_final
            )
        )

    @staticmethod
    def obter_total_novos_casos(
        db: Session,
        data_inicial: date,
        data_final: date
    ) -> int:
        # Conta os casos cuja data de abertura pertence ao período informado.
        return DashboardRepository._contar(
            db.query(func.count(CasoJuridico.id_caso))
            .filter(
                CasoJuridico.data_abertura >= data_inicial,
                CasoJuridico.data_abertura <= data_final
            )
        )

    @staticmethod
    def obter_total_casos_ativos(db: Session) -> int:
        # Conta todos os casos que ainda não foram encerrados.
        return DashboardRepository._contar(
            db.query(func.count(CasoJuridico.id_caso))
            .filter(CasoJuridico.situacao != "Encerrado")
        )

    @staticmethod
    def obter_total_casos_encerrados(
        db: Session,
        data_inicial: date,
        data_final: date
    ) -> int:
        # Conta os casos encerrados dentro do período selecionado.
        return DashboardRepository._contar(
            db.query(func.count(CasoJuridico.id_caso))
            .filter(
                CasoJuridico.situacao == "Encerrado",
                CasoJuridico.data_encerramento >= data_inicial,
                CasoJuridico.data_encerramento <= data_final
            )
        )

    @staticmethod
    def obter_total_atividades_pendentes(db: Session) -> int:
        # Conta atividades pendentes ou em andamento, somente em casos ativos.
        return DashboardRepository._contar(
            db.query(func.count(Atividade.id_atividade))
            .join(
                CasoJuridico,
                CasoJuridico.id_caso == Atividade.id_caso
            )
            .filter(
                Atividade.situacao.in_([
                    "Pendente",
                    "Em andamento"
                ]),
                CasoJuridico.situacao != "Encerrado"
            )
        )

    @staticmethod
    def obter_total_prazos_proximos(db: Session) -> int:
        # Define o intervalo entre hoje e os próximos sete dias.
        hoje = date.today()
        limite = hoje + timedelta(days=7)

        # Conta prazos pendentes dentro do intervalo e vinculados a casos ativos.
        return DashboardRepository._contar(
            db.query(func.count(Prazo.id_prazo))
            .join(
                CasoJuridico,
                CasoJuridico.id_caso == Prazo.id_caso
            )
            .filter(
                Prazo.data_limite >= hoje,
                Prazo.data_limite <= limite,
                Prazo.situacao == "Pendente",
                CasoJuridico.situacao != "Encerrado"
            )
        )

    @staticmethod
    def obter_total_prazos_vencidos(db: Session) -> int:
        # Obtém a data atual para identificar os prazos vencidos.
        hoje = date.today()

        # Conta prazos atrasados que ainda estão pendentes ou marcados como vencidos.
        return DashboardRepository._contar(
            db.query(func.count(Prazo.id_prazo))
            .join(
                CasoJuridico,
                CasoJuridico.id_caso == Prazo.id_caso
            )
            .filter(
                Prazo.data_limite < hoje,
                Prazo.situacao.in_(["Pendente", "Vencido"]),
                CasoJuridico.situacao != "Encerrado"
            )
        )

    @staticmethod
    def obter_casos_por_situacao(db: Session) -> list[dict]:
        # Agrupa os casos pela situação e contabiliza cada grupo.
        resultados = (
            db.query(
                CasoJuridico.situacao,
                func.count(CasoJuridico.id_caso)
            )
            .group_by(CasoJuridico.situacao)
            .all()
        )

        # Organiza os resultados no formato utilizado pelo dashboard.
        return [
            {
                "identificador": None,
                "nome": situacao,
                "quantidade": quantidade
            }
            for situacao, quantidade in resultados
        ]

    @staticmethod
    def obter_casos_por_aluno(db: Session) -> list[dict]:
        # Conta os casos ativos atribuídos a cada aluno.
        resultados = (
            db.query(
                Aluno.id_aluno,
                Usuario.nome,
                func.count(CasoJuridico.id_caso)
            )
            .join(
                Usuario,
                Usuario.id_usuario == Aluno.id_usuario
            )
            .outerjoin(
                CasoJuridico,
                (
                    CasoJuridico.id_aluno_responsavel
                    == Aluno.id_aluno
                )
                & (CasoJuridico.situacao != "Encerrado")
            )
            .group_by(Aluno.id_aluno, Usuario.nome)
            .all()
        )

        # Retorna os dados agrupados por aluno.
        return [
            {
                "identificador": id_aluno,
                "nome": nome,
                "quantidade": quantidade
            }
            for id_aluno, nome, quantidade in resultados
        ]

    @staticmethod
    def obter_casos_por_professor(db: Session) -> list[dict]:
        # Conta os casos orientados por cada professor.
        resultados = (
            db.query(
                Professor.id_professor,
                Usuario.nome,
                func.count(CasoJuridico.id_caso)
            )
            .join(
                Usuario,
                Usuario.id_usuario == Professor.id_usuario
            )
            .outerjoin(
                CasoJuridico,
                CasoJuridico.id_professor_orientador
                == Professor.id_professor
            )
            .group_by(Professor.id_professor, Usuario.nome)
            .all()
        )

        # Retorna os quantitativos agrupados por professor.
        return [
            {
                "identificador": id_professor,
                "nome": nome,
                "quantidade": quantidade
            }
            for id_professor, nome, quantidade in resultados
        ]

    @staticmethod
    def obter_atendimentos_por_aluno(
        db: Session,
        data_inicial: date,
        data_final: date
    ) -> list[dict]:

        # Conta os atendimentos registrados por cada aluno no período informado.
        resultados = (
            db.query(
                Aluno.id_aluno,
                Usuario.nome,
                func.count(Atendimento.id_atendimento)
            )
            .join(
                Usuario,
                Usuario.id_usuario == Aluno.id_usuario
            )
            .outerjoin(
                Atendimento,
                (
                    Atendimento.id_usuario_registro
                    == Aluno.id_usuario
                )
                & (
                    func.date(Atendimento.data_hora)
                    >= data_inicial
                )
                & (
                    func.date(Atendimento.data_hora)
                    <= data_final
                )
            )
            .group_by(Aluno.id_aluno, Usuario.nome)
            .all()
        )

        # Organiza os quantitativos de atendimentos por aluno.
        return [
            {
                "identificador": id_aluno,
                "nome": nome,
                "quantidade": quantidade
            }
            for id_aluno, nome, quantidade in resultados
        ]

    @staticmethod
    def obter_prazos_vencidos(db: Session) -> list[dict]:
        # Identifica prazos atrasados que pertencem a casos não encerrados.
        hoje = date.today()

        resultados = (
            db.query(Prazo)
            .join(
                CasoJuridico,
                CasoJuridico.id_caso == Prazo.id_caso
            )
            .filter(
                Prazo.data_limite < hoje,
                Prazo.situacao.in_(["Pendente", "Vencido"]),
                CasoJuridico.situacao != "Encerrado"
            )
            .order_by(Prazo.data_limite.asc())
            .limit(10)
            .all()
        )

        # Formata os prazos encontrados para a lista de atenção do dashboard.
        return [
            {
                "tipo": "Prazo vencido",
                "id_item": prazo.id_prazo,
                "descricao": prazo.descricao,
                "situacao": prazo.situacao,
                "data_referencia": prazo.data_limite,
                "id_caso": prazo.id_caso
            }
            for prazo in resultados
        ]

    @staticmethod
    def obter_prazos_proximos(db: Session) -> list[dict]:
        # Define o período de consulta dos prazos próximos.
        hoje = date.today()
        limite = hoje + timedelta(days=7)

        resultados = (
            db.query(Prazo)
            .join(
                CasoJuridico,
                CasoJuridico.id_caso == Prazo.id_caso
            )
            .filter(
                Prazo.data_limite >= hoje,
                Prazo.data_limite <= limite,
                Prazo.situacao == "Pendente",
                CasoJuridico.situacao != "Encerrado"
            )
            .order_by(Prazo.data_limite.asc())
            .limit(10)
            .all()
        )

        # Formata os prazos próximos para exibição no dashboard.
        return [
            {
                "tipo": "Prazo próximo",
                "id_item": prazo.id_prazo,
                "descricao": prazo.descricao,
                "situacao": prazo.situacao,
                "data_referencia": prazo.data_limite,
                "id_caso": prazo.id_caso
            }
            for prazo in resultados
        ]

    @staticmethod
    def obter_atividades_pendentes(db: Session) -> list[dict]:
        # Busca atividades pendentes ou em andamento em casos não encerrados.
        resultados = (
            db.query(Atividade)
            .join(
                CasoJuridico,
                CasoJuridico.id_caso == Atividade.id_caso
            )
            .filter(
                Atividade.situacao.in_([
                    "Pendente",
                    "Em andamento"
                ]),
                CasoJuridico.situacao != "Encerrado"
            )
            .order_by(
                Atividade.data_prevista.asc()
            )
            .limit(10)
            .all()
        )

        # Formata as atividades encontradas para a lista de atenção do dashboard.
        return [
            {
                "tipo": "Atividade pendente",
                "id_item": atividade.id_atividade,
                "descricao": atividade.titulo,
                "situacao": atividade.situacao,
                "data_referencia": atividade.data_prevista,
                "id_caso": atividade.id_caso
            }
            for atividade in resultados
        ]
