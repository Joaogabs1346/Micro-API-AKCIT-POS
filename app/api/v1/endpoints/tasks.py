"""
Camada API v1 - Endpoints REST da Tarefa.

Implementa o CRUD HTTP da entidade Task. Cada handler delega a lógica
de persistência para `app.crud.task` e cuida apenas de:
  - Validar o payload (via schemas Pydantic).
  - Resolver dependências (sessão de banco).
  - Traduzir ausência de recurso em HTTP 404.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_db
from app.models.task import TaskStatus
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter()


@router.get(
    "",
    response_model=list[TaskRead],
    summary="Listar tarefas",
    description=(
        "Retorna a lista de tarefas, ordenada da mais recente para a mais "
        "antiga. Aceita filtro opcional por status e paginação via skip/limit."
    ),
)
def read_tasks(
    status_filter: TaskStatus | None = Query(
        default=None,
        alias="status",
        description="Filter tasks by status (pending, in_progress, completed)",
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[TaskRead]:
    """Lista tarefas, opcionalmente filtrando por status.

    Args:
        status_filter: Quando informado, retorna apenas tarefas neste estado.
        skip: Offset para paginação (>= 0).
        limit: Quantidade máxima por página (1–500).
        db: Sessão do banco injetada via `Depends(get_db)`.

    Returns:
        Lista (possivelmente vazia) de tarefas serializadas como `TaskRead`.
    """
    return crud.task.get_multi(db, status=status_filter, skip=skip, limit=limit)


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Buscar tarefa por ID",
    description="Retorna os detalhes de uma única tarefa identificada pelo ID.",
)
def read_task(task_id: int, db: Session = Depends(get_db)) -> TaskRead:
    """Recupera uma tarefa pelo seu identificador.

    Args:
        task_id: Identificador numérico da tarefa.
        db: Sessão do banco injetada via `Depends(get_db)`.

    Returns:
        Tarefa serializada como `TaskRead` (HTTP 200).

    Raises:
        HTTPException: 404 quando a tarefa não existe.
    """
    obj = crud.task.get(db, task_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return obj


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova tarefa",
    description="Cria uma tarefa com status inicial `pending` por padrão.",
)
def create_task(
    payload: TaskCreate, db: Session = Depends(get_db)
) -> TaskRead:
    """Cria uma nova tarefa no banco.

    Args:
        payload: Corpo JSON validado pelo schema `TaskCreate`.
        db: Sessão do banco injetada via `Depends(get_db)`.

    Returns:
        A tarefa recém-criada serializada como `TaskRead` (HTTP 201).
    """
    return crud.task.create(db, obj_in=payload)


@router.put(
    "/{task_id}",
    response_model=TaskRead,
    summary="Atualizar tarefa",
    description=(
        "Atualiza um ou mais campos (title, description, status) de uma tarefa "
        "existente. Campos ausentes no payload são preservados."
    ),
)
def update_task(
    task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)
) -> TaskRead:
    """Aplica atualização parcial nos campos de uma tarefa existente.

    Args:
        task_id: Identificador da tarefa a atualizar.
        payload: Schema `TaskUpdate` com os campos a sobrescrever.
        db: Sessão do banco injetada via `Depends(get_db)`.

    Returns:
        Tarefa atualizada serializada como `TaskRead` (HTTP 200).

    Raises:
        HTTPException: 404 quando a tarefa não existe.
    """
    obj = crud.task.get(db, task_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.task.update(db, db_obj=obj, obj_in=payload)


@router.patch(
    "/{task_id}/complete",
    response_model=TaskRead,
    summary="Marcar tarefa como concluída",
    description="Atalho para definir o status da tarefa como `completed`.",
)
def complete_task(task_id: int, db: Session = Depends(get_db)) -> TaskRead:
    """Marca uma tarefa como concluída.

    Args:
        task_id: Identificador da tarefa a concluir.
        db: Sessão do banco injetada via `Depends(get_db)`.

    Returns:
        Tarefa atualizada com `status="completed"` (HTTP 200).

    Raises:
        HTTPException: 404 quando a tarefa não existe.
    """
    obj = crud.task.get(db, task_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.task.mark_completed(db, db_obj=obj)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover tarefa",
    description="Apaga permanentemente uma tarefa identificada pelo ID.",
)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    """Remove permanentemente uma tarefa do banco.

    Args:
        task_id: Identificador da tarefa a remover.
        db: Sessão do banco injetada via `Depends(get_db)`.

    Returns:
        None. A resposta HTTP é 204 No Content (sem corpo).

    Raises:
        HTTPException: 404 quando a tarefa não existe.
    """
    obj = crud.task.get(db, task_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Task not found")
    crud.task.remove(db, db_obj=obj)
