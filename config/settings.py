from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings


def parse_list(value: str) -> list[str]:
    """Parse a comma-separated env var into a list, handling '*' as a wildcard."""
    if not value:
        return ["*"]
    if value.strip() == "*":
        return ["*"]
    return [v.strip() for v in value.split(",") if v.strip()]


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Food Workspace API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/food_db"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google OAuth / SSO
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None

    # CORS
    ALLOWED_ORIGINS: list[str] = ["*"]

    # Rate Limiting
    RATE_LIMIT_AUTH_CALLS: int = 10
    RATE_LIMIT_AUTH_SECONDS: int = 60

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def validate_allowed_origins(cls, value):
        if isinstance(value, str):
            return parse_list(value)
        return value

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": True}


@lru_cache
def get_settings() -> Settings:
    return Settings()
