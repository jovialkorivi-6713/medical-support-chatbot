import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Resolve the path to the .env file in the root directory
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env")

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    BACKEND_URL: str = "http://localhost:8000"
    
    # Security
    SECRET_KEY: str = "your_super_secret_jwt_key_here"  # Default for dev, override in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    MONGO_URI: str = "mongodb://localhost:27017/mediassist_db" # Use local default if none provided in env
    
    # External APIs
    GEMINI_API_KEY: Optional[str] = None
    
    model_config = SettingsConfigDict(env_file=env_path, env_file_encoding="utf-8", extra="ignore")

settings = Settings()
