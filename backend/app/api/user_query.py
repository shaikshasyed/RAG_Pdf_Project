
from fastapi import APIRouter

from app.services.rag_service import rag_service

router = APIRouter(prefix="/api", tags=["User Query"])


@router.post("/userQuery")
async def user_query(query_text: str, top_k: int = 3):
    results = await rag_service.search_user_query(query_text, top_k=top_k)
    return results

