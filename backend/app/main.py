from fastapi import FastAPI
from app.rag.pdf_loader import load_pdf

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the PDF Reader API"}

@app.get("/read-pdf")
def read_pdf():

    pages = load_pdf("app/uploads/Shaikshavali_Resume.pdf")

    return pages