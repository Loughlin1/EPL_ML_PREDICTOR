from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    DEBUG: bool = False

    DATABASE_URL: str

    ALLOWED_ORIGINS: str = ""

    @field_validator("ALLOWED_ORIGINS")
    def validate_allowed_origins(cls, v: str) -> list[str]:
        return [origin.strip() for origin in v.split(",")] if v else []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()