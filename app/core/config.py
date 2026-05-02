from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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
