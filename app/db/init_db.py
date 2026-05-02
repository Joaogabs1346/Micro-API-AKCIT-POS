"""
Camada DB - Inicialização do Schema.

Cria todas as tabelas registradas em `Base.metadata` usando o engine
configurado. Chamado uma única vez no startup da aplicação (ver
`app.main.create_app`). Para projetos reais com mudanças incrementais
de schema, prefira migrações via Alembic — esta função existe apenas
para simplificar o bootstrap do MVP.
"""

from app.db.base import Base
from app.db.session import engine
from app.models import task  # noqa: F401 - registra metadados do modelo


def init_db() -> None:
    """Cria todas as tabelas declaradas em `Base.metadata` se não existirem.

    Idempotente: chamadas repetidas não recriam nem alteram tabelas
    existentes. Em produção, substitua por migrações Alembic para que
    o schema evolua de forma versionada.

    Returns:
        None.
    """
    Base.metadata.create_all(bind=engine)
