from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-5.4-mini"

    # Google Web Risk
    google_web_risk_api_key: str = ""

    # Database
    database_url: str = "postgresql+asyncpg://smishing:smishing@localhost:5432/smishing_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # API Key (bootstrap seed)
    initial_api_key: str = ""

    # Cache
    url_cache_ttl_hours: int = 24
    url_cache_threat_ttl_hours: int = 1

    # Rate Limiting
    rate_limit_per_minute: int = 60

    # Pipeline
    max_urls_per_message: int = 10
    url_resolve_timeout: float = 5.0
    url_resolve_total_timeout: float = 8.0
    url_max_redirects: int = 10
    web_risk_timeout: float = 3.0
    llm_timeout: float = 10.0
    llm_max_retries: int = 3

    # Circuit Breaker
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: int = 30
    llm_circuit_breaker_failure_threshold: int = 3
    llm_circuit_breaker_recovery_timeout: int = 60

    # Message
    max_message_length: int = 2000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
