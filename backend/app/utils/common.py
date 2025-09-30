from typing import Any, Dict, List
import json
import hashlib

def safe_json_loads(data: str) -> Dict[str, Any]:
    """Safely load JSON data"""
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return {}

def generate_file_hash(content: bytes) -> str:
    """Generate hash for file content"""
    return hashlib.md5(content).hexdigest()

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks"""
    # TODO: Implement text chunking logic
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size-overlap)]
