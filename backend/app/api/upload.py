from fastapi import APIRouter, File, UploadFile

from app.services.rag_service import rag_service

router = APIRouter(prefix="/api", tags=["Upload"])



@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    return await rag_service.upload_pdf(file)