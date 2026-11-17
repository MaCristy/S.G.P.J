
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

    @staticmethod
    def _contar(query) -> int:
        return query.scalar() or 0

    @staticmethod
    def obter_total_atendimentos(
        db: Session,
        data_inicial: date,
        data_final: date
    ) -> int:
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
        return DashboardRepository._contar(
            db.query(func.count(CasoJuridico.id_caso))
            .filter(
                CasoJuridico.data_abertura >= data_inicial,
                CasoJuridico.data_abertura <= data_final
            )
        )

    @staticmethod
    def obter_total_casos_ativos(db: Session) -> int:
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
        return DashboardRepository._contar(
            db.query(func.count(Atividade.id_atividade))
            .filter(
                Atividade.situacao.in_([
                    "Pendente",
                    "Em andamento"
                ])
            )
        )

    @staticmethod
    def obter_total_prazos_proximos(db: Session) -> int:
        hoje = date.today()
        limite = hoje + timedelta(days=7)

        return DashboardRepository._contar(
            db.query(func.count(Prazo.id_prazo))
            .filter(
                Prazo.data_limite >= hoje,
                Prazo.data_limite <= limite,
                Prazo.situacao != "Concluído"
            )
        )

    @staticmethod
    def obter_total_prazos_vencidos(db: Session) -> int:
        hoje = date.today()

        return DashboardRepository._contar(
            db.query(func.count(Prazo.id_prazo))
            .filter(
                Prazo.data_limite < hoje,
                Prazo.situacao != "Concluído"
            )
        )

    @staticmethod
    def obter_casos_por_situacao(db: Session) -> list[dict]:
        resultados = (
            db.query(
                CasoJuridico.situacao,
                func.count(CasoJuridico.id_caso)
            )
            .group_by(CasoJuridico.situacao)
            .all()
        )

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
        hoje = date.today()

        resultados = (
            db.query(Prazo)
            .filter(
                Prazo.data_limite < hoje,
                Prazo.situacao != "Concluído"
            )
            .order_by(Prazo.data_limite.asc())
            .limit(10)
            .all()
        )

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
        hoje = date.today()
        limite = hoje + timedelta(days=7)

        resultados = (
            db.query(Prazo)
            .filter(
                Prazo.data_limite >= hoje,
                Prazo.data_limite <= limite,
                Prazo.situacao != "Concluído"
            )
            .order_by(Prazo.data_limite.asc())
            .limit(10)
            .all()
        )

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
        resultados = (
            db.query(Atividade)
            .filter(
                Atividade.situacao.in_([
                    "Pendente",
                    "Em andamento"
                ])
            )
            .order_by(
                Atividade.data_prevista.asc()
            )
            .limit(10)
            .all()
        )

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
