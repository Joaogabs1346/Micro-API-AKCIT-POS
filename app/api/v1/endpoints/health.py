from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok", "service": "todo-api"}
