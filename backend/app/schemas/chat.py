from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    query_text: str
    document_id: Optional[str] = None