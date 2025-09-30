from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class SQLResponse(BaseModel):
    sql: str
    result: Dict[str, Any]
    rows: List[Dict[str, Any]]
    columns: List[str]
    error: Optional[str] = None
