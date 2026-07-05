from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    query_text: str
    top_k: int = 3
    document_id: Optional[str] = None