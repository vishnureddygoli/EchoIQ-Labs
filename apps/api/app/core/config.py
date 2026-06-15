from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql://echoiq:echoiq@localhost:5432/echoiq"
    redis_url: str = "redis://localhost:6379/0"
    meta_verify_token: str = "dev-meta-token"
    default_client_name: str = "EchoIQ Demo Client"
    default_client_country: str = "US"
    default_client_timezone: str = "America/Chicago"
    mock_calling_enabled: bool = True
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
