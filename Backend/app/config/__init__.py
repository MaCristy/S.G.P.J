
"""
Inicialização do pacote de configurações do S.G.P.J.

Disponibiliza as configurações centralizadas da aplicação
para utilização pelos demais módulos.
"""

from app.config.settings import settings


# Define os recursos disponibilizados pelo pacote.
__all__ = ["settings"]
