from pathlib import Path
import shutil
import uuid

from fastapi import HTTPException, UploadFile

from app.rag.embedding import EmbeddingService
from app.rag.generator import Generator
from app.rag.vector_store import VectorStore

from app.rag.pdf_loader import load_pdf
from app.rag.text_cleaner import clean_text
from app.rag.sentence_chunker import sentence_chunk
from app.rag.prompt_builder import build_prompt

from app.utils.file_hash import generate_file_hash

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
        
        # Read file bytes
        file_bytes = await file.read()

        file_hash = generate_file_hash(file_bytes)

        if self.vector_store.file_exists(file_hash):
            raise HTTPException(
                status_code=400,
                detail="This PDF has already been uploaded."
            )
        
        # Generate a unique document ID
        document_id = str(uuid.uuid4())
        

        # Create uploads folder
        self.upload_folder.mkdir(exist_ok=True)

        # Save PDF
        file_path = self.upload_folder / file.filename

        with open(file_path, "wb") as buffer:
            buffer.write(file_bytes)
        
        pages = load_pdf(file_path)
        total_pages = len(pages)

        self.vector_store.add_document( document_id=document_id, filename=file.filename, file_hash=file_hash, total_pages=total_pages)


        # Clean and chunk text
        for page in pages:
            page["text"] = clean_text(page["text"])
        
        # Create chunks and add to vector store    
        chunks = []
        chunk_id = 1
        for page in pages:
            sentences = sentence_chunk(page["text"])

            for sentence in sentences:
                chunks.append({
                    "document_id": document_id,
                    "chunk_id": chunk_id,
                    "page": page["page"],
                    "text": sentence
                })
                chunk_id += 1

        # Embed chunks and add to vector store
        texts = []
        for chunk in chunks:
            texts.append(chunk["text"])
        
        embeddings = self.embedding_service.embed(texts)

        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding

        self.vector_store.add_chunks(chunks)



        return {
            "message": "PDF uploaded successfully",
            "document_id": document_id,
            "filename": file.filename,
            "total_chunks": len(chunks)
        }
    
    async def search_user_query(self, query_text, document_id=None, top_k=3):
        query_embedding = self.embedding_service.embed([query_text])[0]

        results = self.vector_store.search(query_embedding, document_id = document_id, top_k = top_k)

        for result in results:
            document = self.vector_store.get_document(result["document_id"])
            result["filename"] = document["filename"]

        prompt = build_prompt(query_text, results)

        response = self.generator.generate(prompt)

        return  {
                "answer": response,
                "sources": [
                    {
                        "filename": result["filename"],
                        "page": result["page"]
                    }
                    for result in results
                ]
            }
    
rag_service = RAGService()
        
    