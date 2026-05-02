from app.db.base import Base
from app.db.session import engine
from app.models import task  # noqa: F401 - register model metadata


def init_db() -> None:
    """Create all tables. For real projects, use Alembic migrations instead."""
    Base.metadata.create_all(bind=engine)
