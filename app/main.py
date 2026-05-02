"""
Micro-API de Tarefas - Entry Point.

Ponto único de entrada da aplicação FastAPI. Expõe a função `create_app()`
(application factory) e a instância global `app` consumida pelo Uvicorn.
Conecta as três camadas — configuração (`app.core`), banco (`app.db`) e
roteamento HTTP (`app.api.v1`) — em uma única instância FastAPI.
"""

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.init_db import init_db


def create_app() -> FastAPI:
    """Cria e configura uma instância FastAPI pronta para uso.

    Padrão "application factory": mantém a inicialização explícita e
    permite criar instâncias isoladas em testes. Lê metadados (nome,
    versão, descrição) do objeto `settings`, garante que o schema do
    banco esteja criado e pendura o roteador da v1 sob `/api/v1`.

    Returns:
        Instância FastAPI configurada com router, OpenAPI e endpoint raiz.
    """
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
        """Endpoint raiz informativo — aponta para a documentação Swagger."""
        return {"service": settings.PROJECT_NAME, "docs": "/docs"}

    return application


app = create_app()
