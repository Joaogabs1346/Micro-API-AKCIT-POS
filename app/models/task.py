"""
Camada Models - Modelo ORM da Tarefa.

Define o modelo SQLAlchemy `Task` (mapeado para a tabela `tasks`) e o
enum `TaskStatus` que representa os estados de negócio possíveis.
Esta é a única representação persistente da entidade — schemas Pydantic
em `app.schemas.task` derivam dela para entrada e saída via HTTP.
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    """Retorna o timestamp atual em UTC com timezone-aware datetime."""
    return datetime.now(timezone.utc)


class TaskStatus(str, enum.Enum):
    """Estados possíveis de uma tarefa no fluxo de trabalho."""

    PENDING = "pending"          # Criada, ainda não iniciada
    IN_PROGRESS = "in_progress"  # Em execução
    COMPLETED = "completed"      # Concluída


class Task(Base):
    """Modelo ORM da entidade Tarefa.

    Mapeia a tabela `tasks` no PostgreSQL. Persistido pelo SQLAlchemy 2.x
    com colunas tipadas via `Mapped`/`mapped_column`. Os timestamps são
    preenchidos no servidor de aplicação (não no banco) usando UTC.

    Attributes:
        id: Chave primária autoincrementada.
        title: Título obrigatório (1–200 caracteres). Indexado para busca.
        description: Descrição opcional em texto livre.
        status: Estado atual (pending | in_progress | completed). Indexado
            para suportar filtros por status no `GET /tasks`.
        created_at: Timestamp UTC de criação, preenchido na inserção.
        updated_at: Timestamp UTC da última alteração, atualizado em todo
            UPDATE via `onupdate`.
    """

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
        nullable=False,
    )
