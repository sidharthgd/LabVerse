from pydantic import BaseModel
from typing import Dict, Any, Optional

class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    result: Dict[str, Any]
    type: str
    sources: Optional[list] = None
