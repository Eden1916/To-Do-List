from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TODO_", env_file=".env", extra="ignore"
    )

    database_url: str = "sqlite:///./todo.db"
    cors_origins: list[str] = ["http://localhost:5173"]
