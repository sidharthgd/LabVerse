from pydantic import BaseModel
from typing import List, Dict, Any

class RAGResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    context_used: str
    confidence_score: float
