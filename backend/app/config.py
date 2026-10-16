
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    mongo_url: str = "mongodb://localhost:27017"
    database_name: str = "supportflow"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str
    enable_jobs: bool = True
    access_token_minutes: int = 60
    cookie_secure: bool = False
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore",
    )


settings = Settings()
