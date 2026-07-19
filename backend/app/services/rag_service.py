from pathlib import Path
import shutil
import uuid

from fastapi import HTTPException, UploadFile

from app.rag.conversation_memory import ConversationMemory
from app.rag.memory_resolver import MemoryResolver
from app.rag.embedding import EmbeddingService
from app.rag.generator import Generator
from app.rag.vector_store import VectorStore
from app.rag.query_expander import QueryExpander
from app.rag.multi_query_retriever import MultiQueryRetriever

from app.rag.pdf_loader import load_pdf
from app.rag.text_splitter import split_text
from app.rag.prompt_builder import build_prompt

from app.rag.retrieval_service import RetrievalService
from app.rag.reranker import Reranker
from app.rag.context_compressor import ContextCompressor

from app.utils.file_hash import generate_file_hash
from app.utils.sse import create_sse_event
from app.config import SIMILARITY_THRESHOLD, RETRIEVE_TOP_K, FINAL_TOP_K


class RAGService:

    def __init__(self): 
        
        self.conversation_memory = ConversationMemory()
        self.memory_resolver = MemoryResolver()
        self.embedding_service = EmbeddingService()

        self.vector_store = VectorStore()
        self.query_expander = QueryExpander()
        self.generator = Generator()
        self.reranker = Reranker()
        self.context_compressor = ContextCompressor()

        self.retrieval_service = RetrievalService(vector_store=self.vector_store)
        self.multi_query_retriever = MultiQueryRetriever(retrieval_service=self.retrieval_service, embedding_service=self.embedding_service)

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
        
        
        # Create chunks and add to vector store    
        chunks = []
        chunk_id = 1
        for page in pages:
            page_chunks = split_text(page["text"])

            for chunk in page_chunks:
                chunks.append({
                    "document_id": document_id,
                    "chunk_id": chunk_id,
                    "page": page["page"],
                    "text": chunk
                })
                chunk_id += 1

        # Embed chunks and add to vector store
        texts = [chunk["text"] for chunk in chunks]
        
        embeddings = self.embedding_service.embed(texts)

        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding

        self.vector_store.add_chunks(chunks)
        
        # Refresh the retrieval service index
        self.retrieval_service.refresh_index()


        return {
            "message": "PDF uploaded successfully",
            "document_id": document_id,
            "filename": file.filename,
            "total_chunks": len(chunks)
        }
    
    async def search_user_query(self, query_text, document_id=None):

        recent_history = self.conversation_memory.get_recent_history()
        resolved_query = self.memory_resolver.resolve(query_text, recent_history)
       
        expanded_queries = self.query_expander.expand(resolved_query)
        expanded_queries = list(dict.fromkeys(expanded_queries))

        unique_results = self.multi_query_retriever.retrieve(expanded_queries, document_id=document_id)

        results = self.reranker.rerank(query_text=resolved_query, results=unique_results, top_k=FINAL_TOP_K)

        # compressed_results = self.context_compressor()

    

        # No relevant chunks found
        if not results:
            return {
                "answer": "I couldn't find any relevant information in the uploaded documents.",
                "sources": []
            }

        # Add filename
        for result in results:
            document = self.vector_store.get_document(result["document_id"])
            result["filename"] = document["filename"]

        # print("Filtered results:", results)  # Debugging line to print filtered results
    

        grouped_sources = {}

        for result in results:
            filename = result["filename"]
            if filename not in grouped_sources:
                grouped_sources[filename] = []
            grouped_sources[filename].append(result["page"])

        sources = []
        for filename, pages in grouped_sources.items():
            sources.append({
                "filename": filename,
                "pages": sorted(set(pages))
            })
        
        
        prompt = build_prompt(resolved_query, results)

        try:
            response = self.generator.generate(prompt)
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate response."
            )

        self.conversation_memory.add_user_message(query_text)
        self.conversation_memory.add_assistant_message(response)



        return {
            "answer": response,
             "sources": sources
            }
        

    async def stream_user_query(self, query_text, document_id=None):

        # Get conversation history and resolve the query
        recent_history = self.conversation_memory.get_recent_history()
        resolved_query = self.memory_resolver.resolve(query_text, recent_history)

        # Expand query
        expanded_queries = self.query_expander.expand(resolved_query)
        expanded_queries = list(dict.fromkeys(expanded_queries))

        # Retrieve relevant chunks
        unique_results = self.multi_query_retriever.retrieve(
            expanded_queries,
            document_id=document_id
        )

        # Rerank results
        results = self.reranker.rerank(
            query_text=resolved_query,
            results=unique_results,
            top_k=FINAL_TOP_K
        )

        # No relevant chunks found
        if not results:
            yield "I couldn't find any relevant information in the uploaded documents."
            return

        # Add filename to each result
        for result in results:
            document = self.vector_store.get_document(result["document_id"])
            result["filename"] = document["filename"]

        # Build sources (optional, if you want to use them later)
        grouped_sources = {}

        for result in results:
            filename = result["filename"]
            grouped_sources.setdefault(filename, []).append(result["page"])

        sources = [
            {
                "filename": filename,
                "pages": sorted(set(pages))
            }
            for filename, pages in grouped_sources.items()
        ]

        # Build prompt
        prompt = build_prompt(resolved_query, results)

        full_response = ""

        try:
            # Stream response from the LLM
            stream = self.generator.generate_stream(prompt)

            for chunk in stream:
                full_response += chunk
                
                yield create_sse_event(
                    event = "token",
                    data = {
                        "content":chunk
                        }
                )

            yield create_sse_event(
                    event="sources",
                    data={
                        "sources": grouped_sources
                    }
                )
            
            yield create_sse_event(
                event="done",
                data={}
            )

        except Exception as e:
            yield create_sse_event(
                event="error",
                data={
                    "message": str(e)
                }
            )

        # Save conversation history after streaming completes
        self.conversation_memory.add_user_message(query_text)
        self.conversation_memory.add_assistant_message(full_response)

        
        
   
       
        
rag_service = RAGService()
        
    