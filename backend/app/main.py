from fastapi import FastAPI

from app.api.upload import router as upload_router
from app.api.chat import router as user_query_router

app = FastAPI(title="PDF Chat API")

app.include_router(upload_router)
app.include_router(user_query_router)