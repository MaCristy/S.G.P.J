"""
Pacote de Models ORM (SQLAlchemy) do S.G.P.J.

Cada módulo neste pacote corresponde a uma entidade do banco de dados existente.
Os models mapeiam as tabelas criadas pelo Database/schema.sql sem as recriar.
"""

from app.models.assistido import Assistido
from app.models.atendimento import Atendimento
from app.models.usuario import Usuario
from app.models.caso_juridico import CasoJuridico
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.atividade import Atividade
from app.models.documento import Documento
from app.models.prazo import Prazo
from app.models.historico_caso import HistoricoCaso


__all__ = ["Assistido", "Atendimento", "Usuario", "CasoJuridico", "Aluno", "Professor", "professor_aluno", "Atividade", "Documento", "Prazo", "HistoricoCaso"]