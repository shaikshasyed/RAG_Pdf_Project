from pydantic import BaseModel


class UploadResponse(BaseModel):
    message: str
    document_id: str
    filename: str
    total_chunks: int