from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TODO_", env_file=".env", extra="ignore"
    )

    database_url: str = "sqlite:///./todo.db"
    cors_origins: list[str] = ["http://localhost:5173"]
    jwt_secret: SecretStr | None = Field(default=None, min_length=32)
    access_token_minutes: int = Field(default=60, ge=1, le=10080)
