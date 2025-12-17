from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/labverse"

    # OpenAI
    OPENAI_API_KEY: str = ""

    # Claude
    CLAUDE_API_KEY: str = ""

    # Pinecone
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "labverse"

    # LandingAI
    LANDINGAI_API_KEY: str = ""
    LANDINGAI_ADE_LOG: str = "info"

    # Google Cloud
    GOOGLECLOUD_API_KEY: str = ""
    GOOGLECLOUD_PROJECT_ID: str = ""
    GOOGLECLOUD_LOCATION: str = "us"
    GOOGLECLOUD_PROCESSOR_ID: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379"  # Default for local dev

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
        env_file = "../.env"

settings = Settings()