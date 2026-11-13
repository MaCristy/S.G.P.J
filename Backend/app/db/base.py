"""
Metadados e Base Declarativa do SQLAlchemy para o S.G.P.J.

IMPORTANTE:
    Este módulo define APENAS a Base declarativa e importa os models para
    que o SQLAlchemy os registre nos metadados.
    NÃO cria, altera ou exclui tabelas — o schema foi criado via Database/schema.sql.
    O uso de metadata.reflect() é feito exclusivamente para leitura de saúde.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base declarativa compartilhada por todos os models ORM da aplicação.
    Configurada com suporte a utf8mb4 como charset padrão do MySQL.
    """
    pass

