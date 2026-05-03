# 🎯 Tarefa: Gerar UM diagrama Mermaid da arquitetura

## Persona

Você é um arquiteto de software que documenta projetos Python/FastAPI
com diagramas Mermaid. Sua tarefa é gerar UM ÚNICO diagrama Mermaid que
represente, em uma só visão, a arquitetura completa da Micro-API de
Tarefas localizada em:

```
/home/makisekurisu/PosGrad/Micro-API-AKCIT-POS/
```

## Objetivo

Produzir UM ÚNICO arquivo Mermaid em PT-BR que reflita FIELMENTE o
código real (não inventar componentes que não existem). Esse arquivo
deve mostrar, em um único `flowchart`:

- O cliente que consome a API.
- Todas as camadas internas do FastAPI (main → router → endpoints →
  schemas / deps / crud → models → db).
- A infraestrutura do Docker Compose (PostgreSQL + bind mount em
  `./dados`).
- As setas do fluxo de uma requisição típica.

Caminho de saída (UM ÚNICO arquivo):

```
docs/diagrama.mmd
```

## Regras obrigatórias

### 1. UM arquivo só

Nada de pasta `diagrams/`, nada de README extra, nada de múltiplos `.mmd`.
Apenas `docs/diagrama.mmd`.

### 2. Leia o código real antes de desenhar

ANTES de escrever o diagrama, LEIA estes arquivos para basear o diagrama
no código real:

```
app/main.py
app/core/config.py
app/api/deps.py
app/api/v1/router.py
app/api/v1/endpoints/health.py
app/api/v1/endpoints/tasks.py
app/crud/task.py
app/models/task.py
app/schemas/task.py
app/db/base.py
app/db/session.py
app/db/init_db.py
docker-compose.yml
```

### 3. Não invente componentes

NÃO inventar nodes que não existem (cache Redis, fila SQS, workers
assíncronos, autenticação JWT, etc.). Só desenhar o que está no código.

### 4. Idioma

Rótulos em PT-BR. Nomes técnicos (FastAPI, PostgreSQL, SQLAlchemy,
Pydantic, Uvicorn) podem permanecer em inglês.

### 5. Mermaid puro

O arquivo `.mmd` deve ser Mermaid puro (SEM cercas markdown ` ``` `)
para que `mmdc` consiga renderizar direto.

### 6. Estrutura do diagrama

Usar `flowchart TB` (top-to-bottom) com `subgraph` para agrupar camadas,
deixando claro que existem 3 grandes blocos:
1. Cliente
2. Aplicação FastAPI
3. Infraestrutura Docker

## Modelo desejado (estrutura de referência — adaptar nomes ao código real)

```
flowchart TB
    %% ===== Cliente =====
    subgraph Cliente["Cliente HTTP"]
        C[Browser / curl / Swagger UI]
    end

    %% ===== Aplicação FastAPI =====
    subgraph App["Aplicação FastAPI (Uvicorn)"]
        direction TB

        MAIN["main.py<br/>create_app()"]

        subgraph APIv1["Camada API v1"]
            ROUTER["api.v1.router<br/>api_router"]
            ENDP_TASKS["endpoints.tasks<br/>CRUD /tasks"]
            ENDP_HEALTH["endpoints.health<br/>GET /health"]
            DEPS["api.deps<br/>get_db()"]
        end

        subgraph Domain["Camada de Domínio"]
            SCHEMAS["schemas.task<br/>TaskCreate / TaskUpdate / TaskRead"]
            CRUD["crud.task<br/>get / get_multi / create / update<br/>mark_completed / remove"]
            MODELS["models.task<br/>Task + TaskStatus"]
        end

        subgraph DB["Camada DB"]
            DBBASE["db.base<br/>Base (DeclarativeBase)"]
            DBSESSION["db.session<br/>engine + SessionLocal"]
            DBINIT["db.init_db<br/>init_db()"]
        end

        CONFIG["core.config<br/>Settings (.env)"]
    end

    %% ===== Infraestrutura =====
    subgraph Infra["Docker Compose"]
        PG[("PostgreSQL 16<br/>tabela tasks")]
        VOL[("Bind mount<br/>./dados")]
    end

    %% ===== Fluxo =====
    C -->|HTTP JSON| MAIN
    MAIN --> ROUTER
    ROUTER --> ENDP_TASKS
    ROUTER --> ENDP_HEALTH
    ENDP_TASKS -->|valida payload| SCHEMAS
    ENDP_TASKS -->|Depends| DEPS
    ENDP_TASKS --> CRUD
    CRUD --> MODELS
    MODELS --> DBBASE
    DEPS --> DBSESSION
    DBSESSION --> CONFIG
    MAIN -.->|startup| DBINIT
    DBINIT --> DBBASE
    DBSESSION ==>|psycopg2| PG
    PG --- VOL
```

## Validação pós-mudança

### 1. Sintaxe Mermaid válida

Renderizar para SVG e confirmar exit 0:

```bash
npx -y @mermaid-js/mermaid-cli -i docs/diagrama.mmd -o /tmp/diagrama.svg
```

> Se o ambiente bloquear o sandbox do Chromium (Ubuntu 23.10+):
>
> ```bash
> echo '{"args": ["--no-sandbox"]}' > /tmp/puppeteer-config.json
> npx -y @mermaid-js/mermaid-cli -p /tmp/puppeteer-config.json \
>   -i docs/diagrama.mmd -o /tmp/diagrama.svg
> ```

### 2. Sanity check dos testes

Os 31 testes pytest existentes precisam continuar passando (esta tarefa
NÃO altera código de `app/`, é só sanity check):

```bash
docker compose run --rm -v "$(pwd)/tests:/app/tests" api pytest tests/ -v
```

## Entrega esperada

- 1 arquivo novo: `docs/diagrama.mmd`
- Confirmação de que `mmdc` renderizou sem erro.
- Resumo curto em bullets: principais nodes e arestas do diagrama.
