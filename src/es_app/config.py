from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    data_dir: Path = Field(
        default_factory=lambda: Path.home() / ".es_app",
        validation_alias="ES_DATA_DIR",
    )
    ollama_host: str = Field(
        default="http://127.0.0.1:11434",
        validation_alias="OLLAMA_HOST",
    )
    bind_host: str = Field(default="127.0.0.1", validation_alias="ES_BIND")


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    s.data_dir.mkdir(parents=True, exist_ok=True)
    return s
