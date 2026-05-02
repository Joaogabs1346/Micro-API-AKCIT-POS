"""
Camada DB - Declarative Base.

Define a classe `Base` raiz que todos os modelos ORM herdam. Mantém o
mapeamento declarativo do SQLAlchemy 2.x em um único módulo para que a
metadata (`Base.metadata`) seja compartilhada entre app, migrations e
testes.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classe base declarativa compartilhada por todos os modelos ORM.

    Herda de `DeclarativeBase` (SQLAlchemy 2.x). Toda subclasse cria
    automaticamente uma entrada em `Base.metadata`, usada por
    `init_db()` e pelas fixtures de teste para criar/derrubar tabelas.
    """

    pass
