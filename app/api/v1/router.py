"""
Camada API v1 - Router Agregador.

Agrupa todos os sub-roteadores da versão v1 em um único `APIRouter`
exportado como `api_router`. O `app.main` consome este símbolo e o
monta sob o prefixo configurado em `settings.API_V1_PREFIX`.
Versionar a API por prefixo permite introduzir uma futura `v2` sem
quebrar clientes existentes.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health, tasks

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
