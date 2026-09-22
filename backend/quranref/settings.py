from functools import lru_cache

from pydantic import ValidationInfo, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from . import PROJECT_ROOT


class Settings(BaseSettings):
    """Application settings.

    Values come from environment variables first, then from backend/.env.
    Field names map to environment variables case-insensitively.
    """

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=False,
    )

    app_name: str = "QuranRef"
    environment: str

    db_username: str
    db_password: str
    db_name: str
    db_host: str = "localhost"
    db_port: int = 5432

    debug: bool = False

    google_client_id: str = ""
    google_client_secret: str = ""
    jwt_secret_key: str = "change-me-in-production-minimum-32bytes!"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 720
    frontend_url: str = "http://localhost:41149"
    backend_url: str = "http://localhost:41148"

    @computed_field
    @property
    def db_dsn(self) -> str:
        return (
            f"postgresql://{self.db_username}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @field_validator("debug", mode="before")
    @classmethod
    def determine_debug_mode(cls, v: bool | None, vinfo: ValidationInfo) -> bool:
        if isinstance(v, bool):
            return v

        return vinfo.data["environment"] == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
