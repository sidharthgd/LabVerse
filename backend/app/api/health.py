from fastapi import APIRouter
from app.models.db import get_db

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    System health status check
    """
    try:
        # Check database connection
        db = next(get_db())
        # TODO: Add more health checks (Pinecone, storage, etc.)
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }
