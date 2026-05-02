from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.init_db import init_db


def create_app() -> FastAPI:
    """Application factory — keeps initialization explicit and testable."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    )

    init_db()

    application.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @application.get("/", tags=["root"], include_in_schema=False)
    def root() -> dict[str, str]:
        return {"service": settings.PROJECT_NAME, "docs": "/docs"}

    return application


app = create_app()
