from datetime import datetime

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env file FIRST
load_dotenv()


def _current_season() -> str:
    now = datetime.now()
    year = now.year
    # EPL season starts in August
    if now.month >= 8:
        return f"{year}-{year + 1}"
    return f"{year - 1}-{year}"


class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    DEBUG: bool = False

    DATABASE_URL: str
    ALLOWED_ORIGINS: str = ""

    # App specific variables
    FOOTBALL_DATA_BASE_URL: str
    SUPERBRU_TARGET_URL: str
    SUPERBRU_USERNAME: str
    SUPERBRU_PASSWORD: str
    CURRENT_SEASON: str = _current_season()

    @field_validator("ALLOWED_ORIGINS")
    def validate_allowed_origins(cls, v: str) -> list[str]:
        return [origin.strip() for origin in v.split(",")] if v else []

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
