import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "LunaAlign Backend"
    API_V1_STR: str = "/image"
    
    # Path configuration
    TEMP_DIR: Path = BASE_DIR / "temp"
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://chandra-align.vercel.app/",
    ]
    
    # Pipeline Parameters
    MAX_FILE_SIZE_MB: int = 400
    ALLOWED_IMAGE_EXTENSIONS: set[str] = {".png"}
    ALLOWED_XML_EXTENSIONS: set[str] = {".xml"}

    class Config:
        env_file = ".env"

settings = Settings()

# Ensure temporary directory exists
settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)