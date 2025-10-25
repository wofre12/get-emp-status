# app/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict  
from pydantic import Field  

class Settings(BaseSettings):
    DATABASE_URL: str = Field(default="sqlite:///./local.db")
    API_TOKEN: str = Field(..., min_length=1, description="Bearer token required by the API")
    CACHE_TTL_SECONDS: int = Field(default=60)
    LOG_TO_DB: bool = Field(default=True)

   
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=""
    )

settings = Settings()
