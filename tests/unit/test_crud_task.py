"""Testes unitários da camada CRUD (`app/crud/task.py`)."""

from app import crud
from app.models.task import TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


def test_create_task_with_default_status(db_session):
    """
    Input desejado:  TaskCreate(title="Comprar pão", description="Padaria do Zé")
    Output desejado: Task com id != None, title="Comprar pão",
                     description="Padaria do Zé", status=PENDING,
                     created_at e updated_at != None.
    """
    payload = TaskCreate(title="Comprar pão", description="Padaria do Zé")

    task = crud.task.create(db_session, obj_in=payload)

    assert task.id is not None
    assert task.title == "Comprar pão"
    assert task.description == "Padaria do Zé"
    assert task.status == TaskStatus.PENDING
    assert task.created_at is not None
    assert task.updated_at is not None


def test_create_task_with_explicit_status(db_session):
    """
    Input desejado:  TaskCreate(title="Estudar Pydantic", status=TaskStatus.IN_PROGRESS)
    Output desejado: Task.status == TaskStatus.IN_PROGRESS
    """
    payload = TaskCreate(title="Estudar Pydantic", status=TaskStatus.IN_PROGRESS)

    task = crud.task.create(db_session, obj_in=payload)

    assert task.status == TaskStatus.IN_PROGRESS


def test_get_task_returns_existing(db_session):
    """
    Input desejado:  id de uma task previamente criada
    Output desejado: Task com o mesmo id e mesmo title
    """
    created = crud.task.create(db_session, obj_in=TaskCreate(title="Existente"))

    found = crud.task.get(db_session, created.id)

    assert found is not None
    assert found.id == created.id
    assert found.title == "Existente"


def test_get_task_returns_none_when_not_found(db_session):
    """
    Input desejado:  id 9999 (inexistente)
    Output desejado: None
    """
    found = crud.task.get(db_session, 9999)

    assert found is None


def test_get_multi_without_filter_orders_by_creation_desc(db_session):
    """
    Input desejado:  banco com 3 tasks criadas em ordem A, B, C
    Output desejado: lista com 3 elementos na ordem [C, B, A]
                     (ordem por created_at DESC)
    """
    crud.task.create(db_session, obj_in=TaskCreate(title="A"))
    crud.task.create(db_session, obj_in=TaskCreate(title="B"))
    crud.task.create(db_session, obj_in=TaskCreate(title="C"))

    tasks = crud.task.get_multi(db_session)

    assert len(tasks) == 3
    assert [t.title for t in tasks] == ["C", "B", "A"]


def test_get_multi_filtered_by_completed(db_session):
    """
    Input desejado:  banco com 3 tasks (1 PENDING, 2 COMPLETED)
                     filtro status=COMPLETED
    Output desejado: lista com exatamente 2 elementos, todos COMPLETED
    """
    crud.task.create(db_session, obj_in=TaskCreate(title="A", status=TaskStatus.PENDING))
    crud.task.create(db_session, obj_in=TaskCreate(title="B", status=TaskStatus.COMPLETED))
    crud.task.create(db_session, obj_in=TaskCreate(title="C", status=TaskStatus.COMPLETED))

    tasks = crud.task.get_multi(db_session, status=TaskStatus.COMPLETED)

    assert len(tasks) == 2
    assert all(t.status == TaskStatus.COMPLETED for t in tasks)


def test_update_task_partial_keeps_unset_fields(db_session):
    """
    Input desejado:  task com title="Antigo", payload TaskUpdate(status=IN_PROGRESS)
    Output desejado: title="Antigo" (preservado), status=IN_PROGRESS (atualizado)
    """
    task = crud.task.create(db_session, obj_in=TaskCreate(title="Antigo"))

    updated = crud.task.update(
        db_session,
        db_obj=task,
        obj_in=TaskUpdate(status=TaskStatus.IN_PROGRESS),
    )

    assert updated.title == "Antigo"
    assert updated.status == TaskStatus.IN_PROGRESS


def test_mark_completed_flips_status(db_session):
    """
    Input desejado:  task com status=PENDING
    Output desejado: task.status == COMPLETED
    """
    task = crud.task.create(db_session, obj_in=TaskCreate(title="Lavar carro"))
    assert task.status == TaskStatus.PENDING

    completed = crud.task.mark_completed(db_session, db_obj=task)

    assert completed.status == TaskStatus.COMPLETED


def test_remove_task_makes_get_return_none(db_session):
    """
    Input desejado:  task existente
    Output desejado: depois de remove, get(id) retorna None
    """
    task = crud.task.create(db_session, obj_in=TaskCreate(title="Apagar"))
    task_id = task.id

    crud.task.remove(db_session, db_obj=task)

    assert crud.task.get(db_session, task_id) is None
