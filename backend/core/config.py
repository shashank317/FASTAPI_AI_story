from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    DEBUG: bool = False
    DATABASE_URL: str
    ALLOWED_ORIGINS: List[str] = []

    # This is required for the story generator to work.
    # Renamed from GEMINI_API_KEY for consistency with the library.
    GOOGLE_API_KEY: str
    OPENAI_API_KEY: Optional[str] = None

    # OpenAPI metadata
    PROJECT_NAME: str = "Choose Your Own Adventure"
    PROJECT_VERSION: str = "0.1.0"
    PROJECT_DESCRIPTION: str = "AI to generate cool interactive stories"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    def parse_allowed_origins(cls, v: str) -> List[str]:
        return [origin.strip() for origin in v.split(",")] if isinstance(v, str) else v
    
    def get_gemini_api_key(self):
        # Prefer GOOGLE_API_KEY, fallback to OPENAI_API_KEY
        return self.GOOGLE_API_KEY or self.OPENAI_API_KEY

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
