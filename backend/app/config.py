from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./nexus.db"
    REDIS_URL: Optional[str] = None
    SECRET_KEY: str = "supersecretnexusoscorekey321"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
