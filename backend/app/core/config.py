from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # App Settings
    app_name: str = "AI Business Idea Validator"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Database Settings
    database_url: str = "postgresql://user:password@localhost/ai_validator"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    
    # API Settings
    api_prefix: str = "/api"
    api_v1_prefix: str = "/api/v1"
    
    # Security Settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenAI Settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 2000
    
    # Google Gemini Settings
    google_gemini_api_key: str = ""
    gemini_model: str = "gemini-pro"
    
    # AI Provider Selection
    ai_provider: str = "gemini"  # "gemini" or "openai"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
