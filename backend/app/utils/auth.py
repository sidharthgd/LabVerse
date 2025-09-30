from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import Optional

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)) -> Optional[dict]:
    """
    Validate JWT token and return user information
    """
    # TODO: Implement JWT token validation
    return {"user_id": "123", "email": "user@example.com"}

async def require_auth(user = Depends(get_current_user)):
    """Dependency to require authentication"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user
