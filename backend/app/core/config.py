from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """
    Manages application-wide settings by loading them from environment variables.
    """
    PROJECT_NAME: str = "Stock Market Portfolio API"
    API_VERSION: str = "v1"

    # Database configuration
    # The default value is for a local SQLite DB, which is useful for quick tests.
    # For Docker, this will be overridden by the DATABASE_URL in the .env file.
    DATABASE_URL: str = "sqlite:///./test.db"

    # CORS settings
    ALLOWED_ORIGINS: list[str] = ["*"]  # Allows all origins by default

    # JWT/Security settings
    SECRET_KEY: str = "a_very_secret_key_that_should_be_changed"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

@lru_cache
def get_settings() -> Settings:
    """
    Returns the settings instance, cached for performance.
    This function is used as a dependency in the FastAPI application.
    """
    return Settings()