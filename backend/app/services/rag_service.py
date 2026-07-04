from pathlib import Path
import shutil

from fastapi import HTTPException, UploadFile

from app.rag.embedding import EmbeddingService
from app.rag.generator import Generator
from app.rag.vector_store import VectorStore

from app.rag.pdf_loader import load_pdf
from app.rag.text_cleaner import clean_text
from app.rag.sentence_chunker import sentence_chunk
from app.rag.prompt_builder import build_prompt

class RAGService:

    def __init__(self):

        self.embedding_service = EmbeddingService()

        self.vector_store = VectorStore()

        self.generator = Generator()


        self.upload_folder = Path("uploads")

    
    async def upload_pdf(self, file: UploadFile):

        # Validate
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed."
            )
        
        self.vector_store.reset_collection()

        # Create uploads folder
        self.upload_folder.mkdir(exist_ok=True)

        # Save PDF
        file_path = self.upload_folder / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        pages = load_pdf(file_path)

        for page in pages:
            page["text"] = clean_text(page["text"])
            
        chunks = []
        chunk_id = 1
        for page in pages:
            sentences = sentence_chunk(page["text"])

            for sentence in sentences:
                chunks.append({
                    "chunk_id": chunk_id,
                    "page": page["page"],
                    "text": sentence
                })
                chunk_id += 1

        
        texts = []

        for chunk in chunks:
            texts.append(chunk["text"])

        
        embeddings = self.embedding_service.embed(texts)

        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding

        self.vector_store.add_chunks(chunks)



        return {
            "message": "PDF indexed successfully",
            "pages": len(pages),
            "chunks": len(chunks),
            "status": "Stored in ChromaDB"
        }
    
    async def search_user_query(self, query_text, top_k=3):
        query_embedding = self.embedding_service.embed([query_text])[0]

        results = self.vector_store.search(query_embedding, top_k=top_k)

        prompt = build_prompt(query_text, results)

        response = self.generator.generate(prompt)

        return response
    
rag_service = RAGService()
        
    