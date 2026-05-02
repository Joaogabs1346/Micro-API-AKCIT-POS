"""Testes E2E dos endpoints REST do FastAPI."""

from app.core.config import settings

API = settings.API_V1_PREFIX
TASKS = f"{API}/tasks"


def test_create_task_returns_201_and_full_body(client):
    """
    POST /api/v1/tasks
    Body: {"title": "Estudar Docker Compose", "description": "Ler a documentação oficial"}
    Esperado: 201 + body com id, title, description, status="pending",
              created_at e updated_at em formato ISO 8601.
    """
    response = client.post(
        TASKS,
        json={
            "title": "Estudar Docker Compose",
            "description": "Ler a documentação oficial",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert isinstance(body["id"], int)
    assert body["title"] == "Estudar Docker Compose"
    assert body["description"] == "Ler a documentação oficial"
    assert body["status"] == "pending"
    assert "created_at" in body and "T" in body["created_at"]
    assert "updated_at" in body and "T" in body["updated_at"]


def test_create_task_with_empty_title_returns_422(client):
    """
    POST /api/v1/tasks  body: {"title": ""}
    Esperado: 422, detail apontando para o campo title.
    """
    response = client.post(TASKS, json={"title": ""})

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any("title" in str(err.get("loc", "")) for err in detail)


def test_list_tasks_when_empty_returns_empty_array(client):
    """
    GET /api/v1/tasks  (banco vazio)
    Esperado: 200 + body [].
    """
    response = client.get(TASKS)

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filtered_by_status_completed(client):
    """
    Cenário: 2 tasks pending + 1 completed.
    GET /api/v1/tasks?status=completed
    Esperado: 200 + 1 elemento, todos com status="completed".
    """
    client.post(TASKS, json={"title": "A", "status": "pending"})
    client.post(TASKS, json={"title": "B", "status": "pending"})
    client.post(TASKS, json={"title": "C", "status": "completed"})

    response = client.get(f"{TASKS}?status=completed")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert all(t["status"] == "completed" for t in body)


def test_get_task_by_id_returns_200(client):
    """
    GET /api/v1/tasks/{id} de uma task existente.
    Esperado: 200 + body com o mesmo id.
    """
    created = client.post(TASKS, json={"title": "Achar"}).json()

    response = client.get(f"{TASKS}/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_task_by_id_when_missing_returns_404(client):
    """
    GET /api/v1/tasks/9999 (inexistente)
    Esperado: 404, detail "Task not found".
    """
    response = client.get(f"{TASKS}/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_update_task_changes_title_and_status(client):
    """
    PUT /api/v1/tasks/{id}  body: {"title": "Título atualizado", "status": "in_progress"}
    Esperado: 200 + body com title e status atualizados.
    """
    created = client.post(TASKS, json={"title": "Original"}).json()

    response = client.put(
        f"{TASKS}/{created['id']}",
        json={"title": "Título atualizado", "status": "in_progress"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Título atualizado"
    assert body["status"] == "in_progress"
    assert body["id"] == created["id"]


def test_update_task_when_missing_returns_404(client):
    """
    PUT /api/v1/tasks/9999  body: {"title": "qualquer"}
    Esperado: 404.
    """
    response = client.put(f"{TASKS}/9999", json={"title": "qualquer"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_complete_task_via_patch_sets_status_completed(client):
    """
    PATCH /api/v1/tasks/{id}/complete em task pending
    Esperado: 200 + body com status="completed".
    """
    created = client.post(TASKS, json={"title": "Concluir"}).json()
    assert created["status"] == "pending"

    response = client.patch(f"{TASKS}/{created['id']}/complete")

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_complete_task_when_missing_returns_404(client):
    """
    PATCH /api/v1/tasks/9999/complete
    Esperado: 404.
    """
    response = client.patch(f"{TASKS}/9999/complete")

    assert response.status_code == 404


def test_delete_task_returns_204_then_get_returns_404(client):
    """
    DELETE /api/v1/tasks/{id}
    Esperado: 204 + body vazio.
    Em seguida, GET no mesmo id deve retornar 404.
    """
    created = client.post(TASKS, json={"title": "Apagar"}).json()

    delete_response = client.delete(f"{TASKS}/{created['id']}")

    assert delete_response.status_code == 204
    assert delete_response.text == ""

    follow_up = client.get(f"{TASKS}/{created['id']}")
    assert follow_up.status_code == 404


def test_delete_task_when_missing_returns_404(client):
    """
    DELETE /api/v1/tasks/9999
    Esperado: 404.
    """
    response = client.delete(f"{TASKS}/9999")

    assert response.status_code == 404


def test_health_endpoint_returns_ok(client):
    """
    GET /api/v1/health
    Esperado: 200 + body {"status": "ok", "service": "todo-api"}.
    """
    response = client.get(f"{API}/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "todo-api"}
