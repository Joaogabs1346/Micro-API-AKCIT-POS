"""
Camada Core - Configuração da Aplicação.

Centraliza todas as variáveis de ambiente e metadados do projeto em uma
única classe `Settings` baseada em `pydantic-settings`. Valores são lidos
do arquivo `.env` (quando presente) e podem ser sobrescritos por env vars
do sistema operacional ou do Docker Compose.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuração tipada da aplicação, carregada via pydantic-settings.

    Lê variáveis do `.env` (se existir) e do ambiente do processo. Cada
    atributo tem default sensato, então a aplicação sobe mesmo sem `.env`
    presente — útil para testes locais e CI.

    Attributes:
        PROJECT_NAME: Nome exibido no Swagger e no endpoint raiz.
        DESCRIPTION: Descrição longa exibida na documentação OpenAPI.
        VERSION: Versão semântica do projeto (usada no schema OpenAPI).
        API_V1_PREFIX: Prefixo base de todas as rotas da v1 (ex.: `/api/v1`).
        DATABASE_URL: URL de conexão SQLAlchemy. Em produção aponta para
            PostgreSQL (`postgresql+psycopg2://...`); o default SQLite é
            apenas para conveniência em desenvolvimento local.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Micro-API de Gerenciamento de Tarefas"
    DESCRIPTION: str = (
        "Uma API RESTful simples que permite criar, ler, atualizar e excluir "
        "tarefas. Suporta marcar tarefas como concluídas e filtrar por status."
    )
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./todo.db"


settings = Settings()
