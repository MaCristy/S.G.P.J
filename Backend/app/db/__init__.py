
"""
Inicialização do pacote de banco de dados do S.G.P.J.

Disponibiliza os principais recursos de conexão e gerenciamento
de sessões utilizados pela aplicação.
"""

from app.db.session import get_db, engine


# Define os recursos disponibilizados pelo pacote.
__all__ = ["get_db", "engine"]
