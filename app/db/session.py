"""
Camada DB - Engine e Session Factory.

Cria o engine SQLAlchemy a partir de `settings.DATABASE_URL` e exporta
`SessionLocal`, a fábrica de sessões consumida pela dependency
`get_db`. Aplica o ajuste `check_same_thread=False` apenas quando o
banco é SQLite (necessário porque o FastAPI atende requisições em
threads diferentes da que abriu a conexão).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

connect_args: dict = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
