from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "spur ai chat"
    database_url: str = "sqlite:///./dev.db"
    frontend_origin: str = "http://localhost:5173"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    llm_timeout_seconds: int = 12
    max_input_chars: int = 2000
    history_limit: int = 12
    max_output_tokens: int = 300
    rate_limit_per_ip_per_minute: int = 20
    rate_limit_per_session_per_minute: int = 10
    daily_token_budget_per_session: int = Field(default=20_000)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
