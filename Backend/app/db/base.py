
"""
Base declarativa do SQLAlchemy para o S.G.P.J.

Este módulo define a classe Base compartilhada pelos modelos ORM.
Os modelos utilizam essa classe para registrar suas tabelas nos
metadados do SQLAlchemy.

A estrutura do banco de dados é gerenciada pelo arquivo
Database/schema.sql, não por este módulo.
"""

from sqlalchemy.orm import DeclarativeBase


# Define a base declarativa compartilhada pelos modelos ORM.
class Base(DeclarativeBase):
    pass
