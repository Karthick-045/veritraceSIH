import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "VeriTrace"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'veritrace.db'}")
    
    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "veritrace-super-secret-key-change-in-production-2026-sih")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", str(BASE_DIR / "storage"))
    
    # Rules & Thresholds
    LOW_CONFIDENCE_THRESHOLD: float = float(os.getenv("LOW_CONFIDENCE_THRESHOLD", "0.65"))
    FUZZY_MATCH_THRESHOLD: float = float(os.getenv("FUZZY_MATCH_THRESHOLD", "85.0"))
    
    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173")

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
