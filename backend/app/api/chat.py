
from fastapi import APIRouter
from app.schemas.chat import ChatRequest

from app.services.rag_service import rag_service

router = APIRouter(prefix="/api", tags=["User Query"])


@router.post("/userQuery")
async def user_query(request: ChatRequest):

    results = await rag_service.search_user_query(
        query_text=request.query_text,
        document_id=request.document_id
    )

    return results

