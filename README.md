# Micro-API de Gerenciamento de Tarefas

Micro-API RESTful desenvolvida em **FastAPI + SQLAlchemy 2.x + PostgreSQL**, empacotada com **Docker Compose** e coberta por testes automatizados (unitários, E2E e de schemas) com **pytest**. Projeto entregue como MVP acadêmico para o AKCIT (Pós-Graduação).



---

## Arquitetura

O projeto segue arquitetura em camadas, espelhando a separação clássica do FastAPI:

- **API (`app/api/v1/`)** — roteador, endpoints HTTP e dependências (injeção de sessão).
- **Domínio (`app/schemas/`, `app/crud/`, `app/models/`)** — schemas Pydantic, lógica CRUD e modelos ORM.
- **DB (`app/db/`)** — engine SQLAlchemy, `SessionLocal`, base declarativa e bootstrap (`init_db`).
- **Core (`app/core/config.py`)** — configuração tipada via `pydantic-settings` (lê `.env`).
- **Infra (`docker-compose.yml`)** — Postgres 16-alpine + container da API com healthcheck.

Veja o diagrama detalhado em [docs/diagrama.mmd](docs/diagrama.mmd).

---

## Escopo

CRUD de tarefas com 6 endpoints REST sob o prefixo `/api/v1`:

| Operação | Método | Rota |
|---|---|---|
| Criar tarefa | `POST` | `/api/v1/tasks` |
| Listar tarefas (com filtro por status) | `GET` | `/api/v1/tasks` |
| Buscar tarefa por ID | `GET` | `/api/v1/tasks/{id}` |
| Atualizar tarefa (parcial) | `PUT` | `/api/v1/tasks/{id}` |
| Marcar como concluída | `PATCH` | `/api/v1/tasks/{id}/complete` |
| Remover tarefa | `DELETE` | `/api/v1/tasks/{id}` |

Mais o endpoint utilitário `GET /api/v1/health` (liveness probe).

---

## Tecnologias utilizadas

- **Python 3.12**
- **FastAPI 0.115** — framework web/ASGI
- **Uvicorn 0.32** (com extras `[standard]`) — servidor ASGI
- **SQLAlchemy 2.0.35** — ORM com tipagem `Mapped`/`mapped_column`
- **Pydantic 2.9** + **pydantic-settings 2.5** — validação e config tipada
- **PostgreSQL 16-alpine** — banco de produção
- **psycopg2-binary 2.9** — driver Postgres
- **Docker Compose** — orquestração local
- **pytest 8.3** + **pytest-cov 5.0** + **httpx 0.27** — testes automatizados

---

## Requisitos

- **Docker** e **Docker Compose** (recomendado)
- ou **Python 3.12+** com `pip` (caminho local)

---

## Instalação

### Com Docker (recomendado)

Não exige instalação prévia — apenas Docker:

```bash
git clone <url-do-repo>
cd Micro-API-AKCIT-POS
cp .env.example .env   # opcional; defaults funcionam
docker compose up --build
```

### Localmente (sem Docker)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> **Nota:** rodando local, será necessário um Postgres acessível ou ajustar `DATABASE_URL` para SQLite no `.env`.

---

## Como executar

### Subindo a API

**Com Docker:**
```bash
docker compose up
```

**Localmente:**
```bash
uvicorn app.main:app --reload
```

### Acesso

- API: `http://localhost:8000`
- Documentação Swagger: `http://localhost:8000/docs`
- Documentação ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/api/v1/openapi.json`

---

## Endpoints da API

> Os exemplos a seguir são extraídos diretamente da suíte de testes E2E (`tests/e2e/test_tasks_endpoints.py`). Todos podem ser executados com a API rodando em `http://localhost:8000`.

### `GET /api/v1/health` — Health check

Liveness probe. Não consulta o banco.

**Requisição:**
```bash
curl -i http://localhost:8000/api/v1/health
```

**Resposta esperada (200 OK):**
```json
{
  "status": "ok",
  "service": "todo-api"
}
```

---

### `POST /api/v1/tasks` — Criar tarefa

Cria uma nova tarefa. Status inicial padrão: `pending`.

**Requisição:**
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Estudar Docker Compose","description":"Ler a documentação oficial"}'
```

**Resposta esperada (201 Created):**
```json
{
  "id": 1,
  "title": "Estudar Docker Compose",
  "description": "Ler a documentação oficial",
  "status": "pending",
  "created_at": "2026-05-02T20:34:02.066762Z",
  "updated_at": "2026-05-02T20:34:02.066766Z"
}
```

**Erro de validação (título vazio):**
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":""}'
```

**Resposta esperada (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```

---

### `GET /api/v1/tasks` — Listar tarefas

Lista tarefas ordenadas da mais recente para a mais antiga. Aceita filtro por status e paginação (`skip`, `limit`).

**Requisição (todas):**
```bash
curl http://localhost:8000/api/v1/tasks
```

**Resposta esperada (200 OK) — banco vazio:**
```json
[]
```

**Requisição (filtrando por status):**
```bash
curl "http://localhost:8000/api/v1/tasks?status=completed"
```

**Resposta esperada (200 OK):**
```json
[
  {
    "id": 3,
    "title": "C",
    "description": null,
    "status": "completed",
    "created_at": "2026-05-02T20:35:00.000000Z",
    "updated_at": "2026-05-02T20:35:00.000000Z"
  }
]
```

---

### `GET /api/v1/tasks/{id}` — Buscar tarefa por ID

**Requisição:**
```bash
curl http://localhost:8000/api/v1/tasks/1
```

**Resposta esperada (200 OK):**
```json
{
  "id": 1,
  "title": "Estudar Docker Compose",
  "description": "Ler a documentação oficial",
  "status": "pending",
  "created_at": "2026-05-02T20:34:02.066762Z",
  "updated_at": "2026-05-02T20:34:02.066766Z"
}
```

**Quando o ID não existe:**
```bash
curl -i http://localhost:8000/api/v1/tasks/9999
```

**Resposta esperada (404 Not Found):**
```json
{
  "detail": "Task not found"
}
```

---

### `PUT /api/v1/tasks/{id}` — Atualizar tarefa

Atualização parcial: campos ausentes no payload são preservados.

**Requisição:**
```bash
curl -X PUT http://localhost:8000/api/v1/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Título atualizado","status":"in_progress"}'
```

**Resposta esperada (200 OK):**
```json
{
  "id": 1,
  "title": "Título atualizado",
  "description": "Ler a documentação oficial",
  "status": "in_progress",
  "created_at": "2026-05-02T20:34:02.066762Z",
  "updated_at": "2026-05-02T20:36:11.123456Z"
}
```

**Quando o ID não existe (404 Not Found):**
```json
{
  "detail": "Task not found"
}
```

---

### `PATCH /api/v1/tasks/{id}/complete` — Marcar como concluída

Atalho dedicado para definir `status="completed"`.

**Requisição:**
```bash
curl -X PATCH http://localhost:8000/api/v1/tasks/1/complete
```

**Resposta esperada (200 OK):**
```json
{
  "id": 1,
  "title": "Título atualizado",
  "description": "Ler a documentação oficial",
  "status": "completed",
  "created_at": "2026-05-02T20:34:02.066762Z",
  "updated_at": "2026-05-02T20:37:05.987654Z"
}
```

---

### `DELETE /api/v1/tasks/{id}` — Remover tarefa

**Requisição:**
```bash
curl -i -X DELETE http://localhost:8000/api/v1/tasks/1
```

**Resposta esperada (204 No Content):**
```
HTTP/1.1 204 No Content
(corpo vazio)
```

**Confirmação (a tarefa não existe mais):**
```bash
curl -i http://localhost:8000/api/v1/tasks/1
# 404 Not Found  →  {"detail":"Task not found"}
```

---

## Como rodar os testes

A suíte tem **31 testes** divididos em três categorias:

- `tests/unit/` — 9 testes unitários da camada CRUD (SQLite em memória).
- `tests/e2e/` — 13 testes end-to-end dos endpoints HTTP via `TestClient`.
- `tests/schemas/` — 9 testes de validação dos schemas Pydantic.

### Com Docker

```bash
docker compose run --rm -v "$(pwd)/tests:/app/tests" api pytest tests/ -v
```

> **Nota:** o `.dockerignore` exclui `tests/` da imagem (mantém produção enxuta), por isso o `-v` monta a pasta no container em runtime.

Filtros úteis:

```bash
# Só unitários
docker compose run --rm -v "$(pwd)/tests:/app/tests" api pytest tests/unit -v

# Só E2E
docker compose run --rm -v "$(pwd)/tests:/app/tests" api pytest tests/e2e -v

# Só schemas
docker compose run --rm -v "$(pwd)/tests:/app/tests" api pytest tests/schemas -v
```

### Localmente

```bash
pytest                     # tudo
pytest tests/unit -v       # só unit
pytest tests/e2e -v        # só E2E
pytest tests/schemas -v    # só schemas
pytest -k "complete"       # filtro por nome
```

### Atalhos via Makefile

```bash
make test           # pytest local
make docker-test    # pytest no container
make coverage       # gera relatório HTML em docs/cov_html/
```

---

## Cobertura de Testes

Para gerar o relatório de cobertura em HTML:

```bash
pytest --cov=app --cov-report=html:docs/cov_html --cov-report=term
# ou
make coverage
```

O relatório fica em `docs/cov_html/index.html`.

> **Nota:** a pasta `docs/cov_html/` está no `.gitignore` — não é versionada.

---

## Estrutura do projeto

```
Micro-API-AKCIT-POS/
├── app/
│   ├── api/
│   │   ├── deps.py                 # Dependências (get_db)
│   │   └── v1/
│   │       ├── router.py           # Roteador agregador da v1
│   │       └── endpoints/
│   │           ├── health.py       # GET /health
│   │           └── tasks.py        # CRUD de /tasks
│   ├── core/
│   │   └── config.py               # Settings (pydantic-settings)
│   ├── crud/
│   │   └── task.py                 # Lógica de persistência
│   ├── db/
│   │   ├── base.py                 # DeclarativeBase
│   │   ├── session.py              # engine + SessionLocal
│   │   └── init_db.py              # bootstrap do schema
│   ├── models/
│   │   └── task.py                 # ORM Task + TaskStatus
│   ├── schemas/
│   │   └── task.py                 # TaskCreate, TaskUpdate, TaskRead
│   └── main.py                     # Application factory create_app()
├── tests/
│   ├── conftest.py                 # Fixtures (db_session, client)
│   ├── unit/test_crud_task.py
│   ├── e2e/test_tasks_endpoints.py
│   └── schemas/test_task_schemas.py
├── docs/
│   └── diagrama.mmd                # Diagrama Mermaid da arquitetura
├── dados/                          # Volume bind-mount do Postgres (gitignored)
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .gitignore
├── .dockerignore
├── LICENSE
├── testar-endpoints.sh             # Script de smoke test via curl
└── README.md
```

---

## Documentação

- **Diagrama de arquitetura:** [docs/diagrama.mmd](docs/diagrama.mmd)
- **Swagger UI** (interativa): `http://localhost:8000/docs` com a API rodando
- **ReDoc:** `http://localhost:8000/redoc`
- **Script de smoke test:** [testar-endpoints.sh](testar-endpoints.sh) — exercita os 6 endpoints via `curl` em sequência

---

## Limitações e próximos passos

**Limitações atuais (escopo MVP):**
- Sem autenticação ou autorização (a API é aberta).
- Sem migrations versionadas — o schema é criado via `Base.metadata.create_all` no startup. Em produção real, migrar para Alembic.
- Sem deploy online — execução restrita a `localhost` via Docker.
- Sem rate limiting nem CORS configurado para múltiplos domínios.

**Evoluções planejadas:**
- Autenticação JWT por usuário e isolamento de tarefas por dono.
- Migrations com Alembic.
- Pipeline CI/CD (GitHub Actions) com lint + testes + build da imagem.
- Deploy em provedor cloud (Render / Railway / Fly.io).
- Frontend web simples consumindo a API.

---

## Uso da IA no Desenvolvimento

O desenvolvimento deste projeto contou com o apoio do **Claude Code (Anthropic, modelo Opus 4.7)**, utilizado para:

- **Geração e revisão de código Python** — estrutura FastAPI em camadas (api, crud, models, schemas, db, core), application factory, dependency injection com `get_db`.
- **Geração da suíte de testes automatizados** — 31 testes nas categorias unit / E2E / schemas, com fixtures `db_session` (SQLite em memória + `StaticPool`) e `client` (TestClient com `dependency_overrides`).
- **Geração de docstrings** em PT-BR em todos os módulos, classes e funções de `app/`, com formato Google-style (Args/Returns/Raises) e parâmetros `summary`/`description` nos decorators FastAPI para enriquecer o Swagger.
- **Geração do diagrama Mermaid** da arquitetura em camadas (`docs/diagrama.mmd`).
- **Estruturação do README** e dos artefatos de documentação.
- **Estratégia de commits semânticos** seguindo Conventional Commits (`feat:`, `chore:`, `test:`, `docs:`).

Toda a interação foi feita via **prompts de engenharia estruturada** — role + objetivo + restrições + exemplos literais — para garantir que a saída do modelo refletisse o código real e não invenções.

---

## Licença

Distribuído sob a licença **MIT**. Veja [LICENSE](LICENSE) para o texto completo. Uso acadêmico no contexto do AKCIT / Pós-Graduação.
