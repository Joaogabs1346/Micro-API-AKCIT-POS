"""
Camada Schemas - Schemas Pydantic da Tarefa.

Define os contratos de entrada (`TaskCreate`, `TaskUpdate`) e saída
(`TaskRead`) usados pelos endpoints HTTP. Separa a representação ORM
(em `app.models.task`) do payload trafegado pela API, permitindo
validação, serialização e evolução independentes.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskStatus


class TaskBase(BaseModel):
    """Campos compartilhados entre os schemas de entrada e saída.

    Centraliza as regras de validação (tamanhos, defaults) em um único
    lugar para que `TaskCreate` e `TaskRead` herdem o mesmo contrato.

    Attributes:
        title: Título obrigatório, entre 1 e 200 caracteres.
        description: Descrição opcional em texto livre.
        status: Estado da tarefa, default `TaskStatus.PENDING`.
    """

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(
        default=None, description="Optional longer description of the task"
    )
    status: TaskStatus = Field(
        default=TaskStatus.PENDING, description="Current status of the task"
    )


class TaskCreate(TaskBase):
    """Payload aceito em `POST /tasks` para criar uma nova tarefa.

    Hoje é equivalente a `TaskBase`, mas existe como classe própria para
    permitir evolução independente (ex.: campos só de criação como
    `template_id`) sem quebrar a saída da API.
    """

    pass


class TaskUpdate(BaseModel):
    """Payload aceito em `PUT /tasks/{id}` — todos os campos são opcionais.

    Não herda de `TaskBase` porque os campos têm semântica diferente:
    aqui `None` significa "não alterar". A camada CRUD usa
    `model_dump(exclude_unset=True)` para aplicar apenas o que foi
    explicitamente enviado pelo cliente.

    Attributes:
        title: Novo título (1–200 caracteres) ou None para manter o atual.
        description: Nova descrição ou None para manter a atual.
        status: Novo status ou None para manter o atual.
    """

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus | None = None


class TaskRead(TaskBase):
    """Payload retornado pela API para representar uma tarefa persistida.

    Estende `TaskBase` adicionando os campos gerados pelo banco (`id`,
    `created_at`, `updated_at`). A configuração `from_attributes=True`
    permite criar instâncias a partir de objetos ORM via
    `TaskRead.model_validate(task_orm)`.

    Attributes:
        id: Identificador numérico da tarefa.
        created_at: Timestamp UTC de criação.
        updated_at: Timestamp UTC da última alteração.
    """

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
