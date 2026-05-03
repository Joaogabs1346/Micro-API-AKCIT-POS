# 🎯 Tarefa: Gerar suíte de testes pytest completa

## Persona

Você é uma engenheira Python sênior especializada em testes automatizados de
APIs FastAPI + SQLAlchemy. Você escreve testes determinísticos, isolados,
sem mocks desnecessários, e usa fixtures para evitar duplicação.

## Contexto do projeto

Trata-se de uma **Micro-API REST de gerenciamento de tarefas** já
implementada no repositório atual. Antes de escrever qualquer teste, leia
estes arquivos para entender o domínio:

- `app/main.py` — application factory
- `app/api/v1/endpoints/tasks.py` — endpoints
- `app/api/v1/endpoints/health.py` — health check
- `app/api/deps.py` — dependência `get_db`
- `app/crud/task.py` — funções `get`, `get_multi`, `create`, `update`, `mark_completed`, `remove`
- `app/models/task.py` — modelo ORM `Task` e enum `TaskStatus`
- `app/schemas/task.py` — DTOs `TaskCreate`, `TaskUpdate`, `TaskRead`, `TaskBase`
- `app/db/session.py` — `SessionLocal`, `engine`
- `app/core/config.py` — `Settings.API_V1_PREFIX = "/api/v1"`

**Stack:** FastAPI 0.115, SQLAlchemy 2.0, Pydantic v2, pytest 8.3.

## Objetivo

Gerar **três conjuntos de testes complementares**, organizados em
subpastas dentro de `tests/`:

```
tests/
├── conftest.py              # fixtures compartilhadas
├── unit/                    # conjunto 1
│   └── test_crud_task.py
├── e2e/                     # conjunto 2
│   └── test_tasks_endpoints.py
└── schemas/                 # conjunto 3
    └── test_task_schemas.py
```

---

## Conjunto 1 — Testes unitários (`tests/unit/test_crud_task.py`)

Testar **funções de `app/crud/task.py` em isolamento**, usando uma sessão
SQLAlchemy real apontada para SQLite em memória (não mockar o banco).

**Para cada teste, escrever no docstring um par "Input → Output esperado".**

### Casos obrigatórios

#### 1.1 `create(db, obj_in=TaskCreate(...))`
- **Input desejado:** `TaskCreate(title="Comprar pão", description="Padaria do Zé")`
- **Output desejado:** instância `Task` com `id ≠ None`, `title="Comprar pão"`, `description="Padaria do Zé"`, `status=TaskStatus.PENDING`, `created_at ≠ None`, `updated_at ≠ None`

#### 1.2 `create` com status explícito
- **Input desejado:** `TaskCreate(title="Estudar Pydantic", status=TaskStatus.IN_PROGRESS)`
- **Output desejado:** `Task.status == TaskStatus.IN_PROGRESS`

#### 1.3 `get(db, task_id)` quando existe
- **Input desejado:** id de uma task previamente criada
- **Output desejado:** `Task` com o mesmo id

#### 1.4 `get(db, task_id)` quando não existe
- **Input desejado:** id `9999`
- **Output desejado:** `None`

#### 1.5 `get_multi(db)` sem filtro
- **Input desejado:** banco com 3 tasks (`pending`, `in_progress`, `completed`)
- **Output desejado:** lista com 3 elementos, ordenada por `created_at DESC`

#### 1.6 `get_multi(db, status=TaskStatus.COMPLETED)`
- **Input desejado:** banco com 3 tasks, sendo 2 completed e 1 pending
- **Output desejado:** lista com **2** elementos, todos com `status=COMPLETED`

#### 1.7 `update` parcial
- **Input desejado:** task existente com `title="Antigo"`, payload `TaskUpdate(status=TaskStatus.IN_PROGRESS)`
- **Output desejado:** `Task` com `title="Antigo"` (preservado) e `status=IN_PROGRESS` (atualizado)

#### 1.8 `mark_completed`
- **Input desejado:** task com `status=TaskStatus.PENDING`
- **Output desejado:** `Task.status == TaskStatus.COMPLETED`

#### 1.9 `remove`
- **Input desejado:** task existente
- **Output desejado:** após `remove`, `get(db, task.id)` retorna `None`

---

## Conjunto 2 — Testes E2E (`tests/e2e/test_tasks_endpoints.py`)

Usar `fastapi.testclient.TestClient` com `dependency_overrides` substituindo
`get_db` por uma sessão de teste isolada. **Cada teste é uma request HTTP
real contra a app montada em memória.**

### Caso 2.1 — Adicionar tarefa
```http
POST /api/v1/tasks
Content-Type: application/json

{
  "title": "Estudar Docker Compose",
  "description": "Ler a documentação oficial"
}
```
**Esperado:** status `201`, body com `id` (int), `title="Estudar Docker Compose"`,
`description="Ler a documentação oficial"`, `status="pending"`,
`created_at` e `updated_at` no formato ISO 8601.

### Caso 2.2 — Adicionar tarefa com payload inválido
```http
POST /api/v1/tasks
Content-Type: application/json

{ "title": "" }
```
**Esperado:** status `422`, body contém `detail` apontando para o campo `title`.

### Caso 2.3 — Listar tarefas (vazio)
```http
GET /api/v1/tasks
```
**Esperado:** status `200`, body `[]`.

### Caso 2.4 — Listar tarefas com filtro por status
- Pré-condição: criar 3 tasks via POST com status `pending`, `pending`, `completed`.
```http
GET /api/v1/tasks?status=completed
```
**Esperado:** status `200`, body com **1** elemento, `status="completed"`.

### Caso 2.5 — Atualizar tarefa
- Pré-condição: criar uma task e capturar `id`.
```http
PUT /api/v1/tasks/{id}
Content-Type: application/json

{
  "title": "Título atualizado",
  "status": "in_progress"
}
```
**Esperado:** status `200`, body com `title="Título atualizado"` e
`status="in_progress"`. `updated_at` deve ter avançado em relação ao
`created_at`.

### Caso 2.6 — Atualizar tarefa inexistente
```http
PUT /api/v1/tasks/9999
Content-Type: application/json

{ "title": "qualquer" }
```
**Esperado:** status `404`, body `{"detail": "Task not found"}`.

### Caso 2.7 — Concluir tarefa (atalho PATCH)
- Pré-condição: criar uma task com status default (`pending`).
```http
PATCH /api/v1/tasks/{id}/complete
```
**Esperado:** status `200`, body com `status="completed"`.

### Caso 2.8 — Concluir tarefa inexistente
```http
PATCH /api/v1/tasks/9999/complete
```
**Esperado:** status `404`.

### Caso 2.9 — Remover tarefa
- Pré-condição: criar uma task e capturar `id`.
```http
DELETE /api/v1/tasks/{id}
```
**Esperado:** status `204`, body vazio. Em seguida,
`GET /api/v1/tasks/{id}` deve retornar `404`.

### Caso 2.10 — Remover tarefa inexistente
```http
DELETE /api/v1/tasks/9999
```
**Esperado:** status `404`.

### Caso 2.11 — Health check
```http
GET /api/v1/health
```
**Esperado:** status `200`, body `{"status": "ok", "service": "todo-api"}`.

---

## Conjunto 3 — Testes de schema (`tests/schemas/test_task_schemas.py`)

Testar a **validação Pydantic** em isolamento, sem banco e sem HTTP.
Importar diretamente `TaskCreate`, `TaskUpdate`, `TaskRead`.

### Casos obrigatórios

#### 3.1 `TaskCreate` válido (campos mínimos)
- Input: `{"title": "Tarefa X"}`
- Output: instância com `title="Tarefa X"`, `description=None`, `status=TaskStatus.PENDING`.

#### 3.2 `TaskCreate` válido (todos os campos)
- Input: `{"title": "Tarefa X", "description": "desc", "status": "in_progress"}`
- Output: instância com `status=TaskStatus.IN_PROGRESS`.

#### 3.3 `TaskCreate` inválido — title vazio
- Input: `{"title": ""}`
- Esperado: `pydantic.ValidationError` mencionando `min_length`.

#### 3.4 `TaskCreate` inválido — title > 200 chars
- Input: `{"title": "x" * 201}`
- Esperado: `pydantic.ValidationError` mencionando `max_length`.

#### 3.5 `TaskCreate` inválido — status desconhecido
- Input: `{"title": "X", "status": "abandonada"}`
- Esperado: `pydantic.ValidationError`.

#### 3.6 `TaskUpdate` aceita corpo totalmente vazio
- Input: `{}`
- Output: instância com todos os campos `None`.

#### 3.7 `TaskUpdate` parcial
- Input: `{"status": "completed"}`
- Output: instância com `status=TaskStatus.COMPLETED`, demais campos `None`.

#### 3.8 `TaskRead.model_validate` a partir de objeto SQLAlchemy
- Input: instância de `Task` (ORM) com todos os campos preenchidos
- Output: `TaskRead` com os mesmos valores, sem erro (graças a
  `from_attributes=True`).

---

## Convenções e restrições

1. **Framework**: pytest 8.x. Não usar `unittest.TestCase`.
2. **Sem mocks** para o banco. Usar SQLite em memória
   (`sqlite:///:memory:` ou arquivo descartável).
3. **Fixtures em `tests/conftest.py`**:
   - `db_session`: cria/destrói tabelas a cada teste, yield uma `Session`.
   - `client`: `TestClient(app)` com `dependency_overrides[get_db]` apontando
     para `db_session`. Usar nos testes E2E.
4. **Nomeação**: `test_<o_que_é_testado>_<situação>`.
   Ex: `test_create_task_with_default_status`, `test_get_task_returns_none_when_not_found`.
5. **Asserts específicos**, não genéricos. Use `assert response.status_code == 201`
   em vez de `assert response.ok`.
6. **Cada teste deve passar isoladamente** (sem depender de ordem).
7. **Ignorar warnings de deprecação** em fixtures, mas não suprimi-los no código.
8. Ao final, rodar `pytest -v` e garantir que **todos os testes passam**.

## Formato da saída

1. Conteúdo completo de cada arquivo (não usar `...`).
2. Após o código, um bloco "Como executar" com:
   ```bash
   pytest tests/unit -v
   pytest tests/e2e -v
   pytest tests/schemas -v
   pytest -v   # tudo
   ```
3. Reportar a saída esperada do `pytest -v` (lista de testes, todos PASSED).

## Não faça

- ❌ Não modifique código de produção em `app/`.
- ❌ Não adicione dependências novas além das já em `requirements.txt`.
- ❌ Não escreva docstrings vagos como "testa create" — use o par
  Input/Output desejado.
- ❌ Não use `print()` em testes — assertions falam por si.
