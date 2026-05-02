"""Testes de validação dos schemas Pydantic em `app/schemas/task.py`."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate


def test_task_create_with_minimal_fields_uses_defaults():
    """
    Input desejado:  {"title": "Tarefa X"}
    Output desejado: TaskCreate(title="Tarefa X", description=None,
                                status=TaskStatus.PENDING)
    """
    obj = TaskCreate(title="Tarefa X")

    assert obj.title == "Tarefa X"
    assert obj.description is None
    assert obj.status == TaskStatus.PENDING


def test_task_create_with_all_fields():
    """
    Input desejado:  {"title": "Tarefa X", "description": "desc", "status": "in_progress"}
    Output desejado: TaskCreate com status=TaskStatus.IN_PROGRESS
    """
    obj = TaskCreate(title="Tarefa X", description="desc", status="in_progress")

    assert obj.status == TaskStatus.IN_PROGRESS
    assert obj.description == "desc"


def test_task_create_rejects_empty_title():
    """
    Input desejado:  {"title": ""}
    Esperado: ValidationError mencionando min_length / string_too_short.
    """
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(title="")

    errors = exc_info.value.errors()
    assert any(
        e["loc"] == ("title",) and "string_too_short" in e["type"]
        for e in errors
    )


def test_task_create_rejects_title_above_200_chars():
    """
    Input desejado:  title com 201 caracteres
    Esperado: ValidationError mencionando max_length / string_too_long.
    """
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(title="x" * 201)

    errors = exc_info.value.errors()
    assert any(
        e["loc"] == ("title",) and "string_too_long" in e["type"]
        for e in errors
    )


def test_task_create_rejects_unknown_status():
    """
    Input desejado:  {"title": "X", "status": "abandonada"}
    Esperado: ValidationError no campo status.
    """
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(title="X", status="abandonada")

    errors = exc_info.value.errors()
    assert any(e["loc"] == ("status",) for e in errors)


def test_task_update_accepts_completely_empty_payload():
    """
    Input desejado:  {} (corpo vazio)
    Output desejado: TaskUpdate com todos os campos None.
    """
    obj = TaskUpdate()

    assert obj.title is None
    assert obj.description is None
    assert obj.status is None


def test_task_update_partial_only_sets_provided_fields():
    """
    Input desejado:  {"status": "completed"}
    Output desejado: TaskUpdate(status=COMPLETED) com title e description None.
    """
    obj = TaskUpdate(status="completed")

    assert obj.status == TaskStatus.COMPLETED
    assert obj.title is None
    assert obj.description is None


def test_task_update_dump_excludes_unset_fields():
    """
    Garante o comportamento usado pelo CRUD (model_dump(exclude_unset=True))
    para fazer atualizações parciais.
    Input desejado:  TaskUpdate(status="in_progress")
    Output desejado: model_dump retorna apenas {'status': ...}.
    """
    obj = TaskUpdate(status="in_progress")

    data = obj.model_dump(exclude_unset=True)

    assert data == {"status": TaskStatus.IN_PROGRESS}


def test_task_read_validates_from_orm_object():
    """
    Input desejado:  instância Task (ORM) com todos os campos preenchidos
    Output desejado: TaskRead com os mesmos valores (graças a from_attributes=True).
    """
    now = datetime.now(timezone.utc)
    orm_task = Task(
        id=42,
        title="ORM-backed",
        description="Vem do banco",
        status=TaskStatus.IN_PROGRESS,
        created_at=now,
        updated_at=now,
    )

    dto = TaskRead.model_validate(orm_task)

    assert dto.id == 42
    assert dto.title == "ORM-backed"
    assert dto.description == "Vem do banco"
    assert dto.status == TaskStatus.IN_PROGRESS
    assert dto.created_at == now
    assert dto.updated_at == now
