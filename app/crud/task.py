"""
Camada CRUD - Operações de Persistência da Tarefa.

Concentra toda a lógica de acesso ao banco da entidade Task. Os
endpoints (em `app.api.v1.endpoints.tasks`) chamam estas funções e
ficam livres de SQL/ORM. Cada função recebe a `Session` por injeção
para que a mesma transação possa ser reusada em testes.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


def get(db: Session, task_id: int) -> Task | None:
    """Busca uma tarefa pelo seu identificador.

    Args:
        db: Sessão SQLAlchemy aberta (injetada via dependency).
        task_id: ID numérico da tarefa procurada.

    Returns:
        A instância `Task` correspondente, ou `None` se não existir.
    """
    return db.get(Task, task_id)


def get_multi(
    db: Session,
    *,
    status: TaskStatus | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Task]:
    """Lista tarefas com filtro opcional por status e paginação.

    Args:
        db: Sessão SQLAlchemy aberta.
        status: Quando informado, retorna apenas tarefas neste estado.
        skip: Quantidade de registros a pular (offset). Default 0.
        limit: Quantidade máxima a retornar. Default 100.

    Returns:
        Lista de `Task` ordenada por `created_at` decrescente (mais
        recentes primeiro). Pode ser vazia.
    """
    stmt = select(Task)
    if status is not None:
        stmt = stmt.where(Task.status == status)
    stmt = stmt.order_by(Task.created_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def create(db: Session, *, obj_in: TaskCreate) -> Task:
    """Cria uma nova tarefa no banco e retorna o modelo persistido.

    Args:
        db: Sessão SQLAlchemy aberta.
        obj_in: Dados validados pelo schema `TaskCreate`.

    Returns:
        Instância `Task` já com `id`, `created_at` e `updated_at`
        populados pelo banco após o COMMIT.
    """
    task = Task(
        title=obj_in.title,
        description=obj_in.description,
        status=obj_in.status,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update(db: Session, *, db_obj: Task, obj_in: TaskUpdate) -> Task:
    """Aplica atualização parcial à tarefa e persiste as mudanças.

    Usa `model_dump(exclude_unset=True)` para alterar apenas os campos
    explicitamente enviados pelo cliente — campos ausentes mantêm o
    valor atual.

    Args:
        db: Sessão SQLAlchemy aberta.
        db_obj: Instância `Task` carregada do banco a ser modificada.
        obj_in: Schema `TaskUpdate` com os campos a sobrescrever.

    Returns:
        A mesma instância `Task` recebida, agora com `updated_at`
        renovado e os campos atualizados refletidos.
    """
    data = obj_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def mark_completed(db: Session, *, db_obj: Task) -> Task:
    """Atalho para marcar uma tarefa como concluída.

    Equivalente a chamar `update` com `TaskUpdate(status=COMPLETED)`,
    mas exposto como operação dedicada para refletir o endpoint
    `PATCH /tasks/{id}/complete`.

    Args:
        db: Sessão SQLAlchemy aberta.
        db_obj: Instância `Task` a ser marcada como concluída.

    Returns:
        A tarefa com `status == TaskStatus.COMPLETED` e `updated_at`
        renovado.
    """
    db_obj.status = TaskStatus.COMPLETED
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, db_obj: Task) -> None:
    """Remove permanentemente a tarefa do banco.

    Args:
        db: Sessão SQLAlchemy aberta.
        db_obj: Instância `Task` a ser deletada.

    Returns:
        None.
    """
    db.delete(db_obj)
    db.commit()
