from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import os
import httpx


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://humain:humain_secret@localhost:5432/humain_decisionops"
    mongo_url: str = "mongodb://humain:humain_secret@localhost:27017/"
    
    # Startup behavior
    seed_on_startup: bool = False
    
    # LLM Providers
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    
    # Heuristic mode - disables LLM calls if no provider available
    heuristic_mode: bool = False
    
    # LangSmith
    langsmith_api_key: str = ""
    langsmith_project: str = "humain-decisionops"
    
    # Authentication
    api_key: str = ""
    auth_enabled: bool = False
    
    # CORS
    cors_allow_origins: str = "*"  # Comma-separated list or "*"
    
    # Logging
    log_level: str = "INFO"
    
    # File Storage
    upload_dir: str = "/app/uploads"
    policy_dir: str = "/app/policies"
    
    class Config:
        env_file = ".env"
        extra = "ignore"
    
    @property
    def use_openai(self) -> bool:
        return bool(self.openai_api_key)
    
    @property
    def use_langsmith(self) -> bool:
        return bool(self.langsmith_api_key)
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if self.cors_allow_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]
    
    def check_ollama_available(self) -> bool:
        """Check if Ollama is reachable."""
        if not self.ollama_base_url:
            return False
        try:
            response = httpx.get(f"{self.ollama_base_url}/api/tags", timeout=2.0)
            return response.status_code == 200
        except Exception:
            return False
    
    @property
    def effective_mode(self) -> str:
        """Determine the effective operating mode."""
        if self.heuristic_mode:
            return "heuristic"
        if self.use_openai:
            return "openai"
        if self.check_ollama_available():
            return "ollama"
        # Fallback to heuristic if no LLM available
        return "heuristic"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
