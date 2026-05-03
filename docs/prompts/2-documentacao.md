# 🎯 Tarefa: Documentar o código com docstrings em PT-BR

## Persona

Você é um engenheiro Python sênior especializado em FastAPI e SQLAlchemy.
Sua tarefa é DOCUMENTAR (e somente documentar — não alterar lógica) o código
da Micro-API de Tarefas localizada em:

```
/home/makisekurisu/PosGrad/Micro-API-AKCIT-POS/app/
```

## Objetivo

Adicionar docstrings em PT-BR a TODOS os arquivos `.py` dentro de `app/` para
que qualquer pessoa nova no projeto consiga entender o papel de cada módulo,
classe e função SEM precisar ler o corpo do código.

## Regras obrigatórias

### 1. NÃO alterar nenhuma linha de lógica/código executável

- Não renomear variáveis, não mover imports, não mudar tipos.
- Apenas ADICIONAR (ou substituir, se já existir) docstrings.

### 2. Docstring de módulo em todo arquivo `.py`

TODO arquivo `.py` em `app/` (incluindo `__init__.py` não vazios) deve
começar com um docstring de módulo no formato exato abaixo:

```python
"""
Nome curto do módulo - papel em uma frase.

Parágrafo (2 a 4 linhas) explicando responsabilidade do módulo, que
camada arquitetural ele ocupa (api / schema / model / crud / db / core)
e como ele se conecta com os outros módulos do projeto.
"""
```

Exemplo do estilo desejado (referência visual de formatação):

```python
"""
Lambda Core Proxy - Entry Point.

Single entry point: the Step Function invokes this Lambda with a normalized
event payload. The SQS-direct path was removed in the PR1 refactor (2026-04-29).
"""

from lambdas.step_function_handler import handler

__all__ = ['handler']
```

> Note que o docstring fica ANTES dos imports e que tem 1 linha de título
> curta + 1 linha em branco + corpo explicativo.

### 3. Docstring para classes públicas (Google-style)

TODA classe pública (`Settings`, `Task`, `TaskStatus`, `TaskCreate`, `TaskUpdate`,
`TaskRead`, `Base`) deve ter docstring no formato Google-style:

```python
class Task(Base):
    """Modelo ORM da entidade Tarefa.

    Mapeia a tabela `tasks` no PostgreSQL. Persistido pelo SQLAlchemy 2.x
    com colunas tipadas via `Mapped`/`mapped_column`.

    Attributes:
        id: Chave primária autoincrementada.
        title: Título obrigatório (1–200 caracteres).
        description: Descrição opcional em texto livre.
        status: Estado atual (pending | in_progress | completed).
        created_at: Timestamp UTC de criação, preenchido pelo banco.
        updated_at: Timestamp UTC da última alteração, atualizado em UPDATE.
    """
```

### 4. Docstring para funções públicas (Google-style)

TODA função pública (sem prefixo `_`) deve ter docstring Google-style com:

- 1 linha de resumo (verbo no infinitivo: "Cria...", "Retorna...", "Remove...")
- `Args:` cada parâmetro com tipo lógico + significado
- `Returns:` tipo lógico + significado, ou "None." se for void
- `Raises:` apenas se a função levanta exceção propositalmente (ex.: `HTTPException`)

Exemplo desejado:

```python
def create(db: Session, *, obj_in: TaskCreate) -> Task:
    """Cria uma nova tarefa no banco e retorna o modelo persistido.

    Args:
        db: Sessão SQLAlchemy aberta (injetada via dependency).
        obj_in: Dados validados pelo schema TaskCreate.

    Returns:
        Instância Task já com `id`, `created_at` e `updated_at` populados
        pelo banco após o COMMIT.
    """
```

### 5. Endpoints FastAPI: `summary` e `description` nos decorators

Além do docstring da função, preservar (ou criar, se ausente) os parâmetros
`summary=` e `description=` nos decorators `@router.post`, `@router.get` etc.
Eles aparecem no Swagger.

Exemplo:

```python
@router.post(
    "/",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova tarefa",
    description="Cria uma tarefa com status inicial `pending` por padrão.",
)
def create_task(...) -> TaskRead:
    """Endpoint de criação de tarefa.

    Args:
        payload: Corpo JSON validado pelo schema TaskCreate.
        db: Sessão do banco injetada via Depends(get_db).

    Returns:
        A tarefa recém-criada serializada como TaskRead (HTTP 201).
    """
```

### 6. Enums com comentários inline

Para enums (`TaskStatus`), documentar cada membro com comentário inline curto
explicando o significado de negócio:

```python
class TaskStatus(str, Enum):
    """Estados possíveis de uma tarefa no fluxo de trabalho."""

    PENDING = "pending"          # Criada, ainda não iniciada
    IN_PROGRESS = "in_progress"  # Em execução
    COMPLETED = "completed"      # Concluída
```

### 7. Idioma

PT-BR em TODOS os docstrings (mesmo que o código tenha nomes em inglês).
Tom técnico, direto, sem firulas.

### 8. Tamanho

NÃO escrever romances. Resumo de função em 1 linha; corpo adicional só
se houver invariante, efeito colateral ou regra de negócio não-óbvia.

## Arquivos a documentar (lista exaustiva)

```
app/__init__.py                   (se existir)
app/main.py                       (factory create_app)
app/core/__init__.py              (se existir)
app/core/config.py                (classe Settings)
app/db/__init__.py                (se existir)
app/db/base.py                    (Base = DeclarativeBase)
app/db/session.py                 (engine + SessionLocal)
app/db/init_db.py                 (init_db / create_all)
app/models/__init__.py            (se existir)
app/models/task.py                (Task + TaskStatus)
app/schemas/__init__.py           (se existir)
app/schemas/task.py               (TaskCreate, TaskUpdate, TaskRead)
app/crud/__init__.py              (se existir)
app/crud/task.py                  (get, get_multi, create, update,
                                   mark_completed, remove)
app/api/__init__.py               (se existir)
app/api/deps.py                   (get_db)
app/api/v1/__init__.py            (se existir)
app/api/v1/router.py              (api_router)
app/api/v1/endpoints/__init__.py  (se existir)
app/api/v1/endpoints/health.py    (GET /health)
app/api/v1/endpoints/tasks.py     (CRUD endpoints)
```

## Validação pós-mudança

Depois de aplicar as docstrings, rode:

```bash
cd /home/makisekurisu/PosGrad/Micro-API-AKCIT-POS
docker compose run --rm -v "$(pwd)/tests:/app/tests" api pytest tests/ -v
```

Os 31 testes existentes precisam continuar PASSANDO. Se algum quebrar, é
sinal de que alguma alteração saiu do escopo "só docstring" — reverta.

## Entrega esperada

- Diff somente com adições/substituições de docstrings.
- Resumo final em bullets: quantos arquivos foram tocados e quantas funções/
  classes ganharam docstring.
- Confirmação de que `pytest tests/ -v` ainda dá 31 passed.
