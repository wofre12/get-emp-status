from pydantic import BaseModel
import os

class Settings(BaseModel):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./local.db")
    API_TOKEN: str | None = os.getenv("API_TOKEN")
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "60"))
    LOG_TO_DB: bool = os.getenv("LOG_TO_DB", "1") == "1"

settings = Settings()
