from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "sistemaEpidemiologico API"
    environment: str = "local"
    database_url: str = "postgresql+psycopg://app:app@localhost:5432/sistema_epidemiologico"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 30
    cookie_secure: bool = False
    cookie_domain: str | None = None
    access_cookie_name: str = "se_access_token"
    refresh_cookie_name: str = "se_refresh_token"
    cors_origins: str = "http://localhost:3000"
    auto_create_manager: bool = False
    manager_email: str | None = None
    manager_password: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @field_validator("cookie_domain", mode="before")
    @classmethod
    def blank_cookie_domain_is_none(cls, value: str | None) -> str | None:
        if value == "":
            return None
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
