from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/labverse"
    
    # Pinecone
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "labverse"
    
    # Google Drive
    GOOGLE_DRIVE_CREDENTIALS: str = ""
    
    # Box
    BOX_CLIENT_ID: str = ""
    BOX_CLIENT_SECRET: str = ""
    
    # Storage
    STORAGE_BUCKET: str = "labverse-storage"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    
    class Config:
        env_file = ".env"

settings = Settings()
