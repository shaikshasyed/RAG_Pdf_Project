from fastapi import APIRouter, UploadFile, File

from app.services.rag_service import rag_service
from app.schemas.upload import UploadResponse

router = APIRouter(
    prefix="/api",
    tags=["Upload PDF"]
)


@router.post(
    "/upload",
    response_model=UploadResponse
)
async def upload_pdf(
    file: UploadFile = File(...)
):

    result = await rag_service.upload_pdf(file)

    return result