
"""
Pacote de Models ORM (SQLAlchemy) do S.G.P.J.

Cada módulo deste pacote corresponde a uma entidade do banco de dados.
Os models mapeiam as tabelas existentes sem recriá-las.
"""

# Importa os models para disponibilizá-los pelo pacote.
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

# Importa o model responsável pelas solicitações públicas de cadastro.
from app.models.solicitacao_cadastro import SolicitacaoCadastro 


# Define os models disponibilizados em importações do pacote.
__all__ = [
    "Assistido",
    "Atendimento",
    "Usuario",
    "CasoJuridico",
    "Aluno",
    "Professor",
    "Atividade",
    "Documento",
    "Prazo",
    "HistoricoCaso",
    "SolicitacaoCadastro"
]
