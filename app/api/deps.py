"""
Camada API - Dependências do FastAPI.

Concentra os "providers" injetáveis via `Depends(...)`. Hoje exporta
apenas `get_db`, que abre uma sessão por requisição e garante que ela
seja fechada ao final, mesmo em caso de erro.
"""

from typing import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Dependency do FastAPI que injeta uma sessão SQLAlchemy por requisição.

    Cria uma `Session` a partir de `SessionLocal`, entrega ao endpoint
    via `yield` e garante o `close()` no `finally` — mesmo se o
    handler levantar exceção. Esse padrão equivale a um context
    manager e é o ponto de injeção sobrescrito pelos testes via
    `app.dependency_overrides[get_db]`.

    Yields:
        Sessão SQLAlchemy pronta para uso na duração da requisição.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
