from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class PandasResponse(BaseModel):
    code: str
    result: Dict[str, Any]
    datasets_used: List[str]
    execution_time: float
    error: Optional[str] = None
