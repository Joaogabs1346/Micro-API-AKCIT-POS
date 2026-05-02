"""
Camada API v1 - Endpoint de Health Check.

Expõe `GET /health`, usado por orquestradores (Docker Compose,
Kubernetes) e por testes E2E como liveness probe. Resposta estática
e barata por design — não toca no banco.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/health",
    summary="Health check da aplicação",
    description="Liveness probe que confirma que o processo está respondendo.",
)
def health_check() -> dict[str, str]:
    """Retorna um payload fixo indicando que a aplicação está viva.

    Não consulta o banco propositalmente: serve apenas como liveness
    probe. Para verificar dependências externas, prefira um endpoint
    `/readiness` separado.

    Returns:
        Dicionário com `status="ok"` e o nome do serviço.
    """
    return {"status": "ok", "service": "todo-api"}
