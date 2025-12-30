from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ECHIDNA_AGENT_DB_URL: str
    OPENAI_API_KEY: str
    
    # Agent Models
    AGENT_MODEL_TRIAGE: str = "gpt-4o"
    AGENT_MODEL_FIX: str = "gpt-4o"
    AGENT_MODEL_DEFAULT: str = "gpt-3.5-turbo"

settings = Settings()
