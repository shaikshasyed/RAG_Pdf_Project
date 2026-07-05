import chromadb
from chromadb.config import Settings
from numpy import where
from datetime import datetime

class VectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="chroma_db"
        )

        self.documents = self.client.get_or_create_collection(
            name="documents"
        )

        self.chunks = self.client.get_or_create_collection(
            name="pdf_chunks"
        )
    
    def add_document(self, document_id, filename, file_hash, total_pages):

        # for chunk in chunks:
        #     print(chunk["embedding"][:10])  # Print the first 10 elements of the embedding for debugging

        self.documents.add(
            ids=[document_id],
            documents=[filename],
            metadatas=[{
                "file_hash": file_hash,
                "total_pages": total_pages,
                "uploaded_at": datetime.now().isoformat()
            }]
        )
    
    def add_chunks(self, chunks):

        self.chunks.add(

            ids=[
                str(chunk["chunk_id"])
                for chunk in chunks
            ],

            documents=[
                chunk["text"]
                for chunk in chunks
            ],

            embeddings=[
                chunk["embedding"]
                for chunk in chunks
            ],

            metadatas=[
                {
                    "document_id": chunk["document_id"],
                    "page": chunk["page"],
                    "chunk_id": chunk["chunk_id"]
                }
                for chunk in chunks
            ]
        )        

    def search(self, query_embedding, document_id=None, top_k=3):

        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
        }

        if document_id:
            query_params["where"] = {
                "document_id": document_id
            }

        results = self.chunks.query(**query_params)

        formatted_results = []

        for doc, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            formatted_results.append({
                "text": doc,
                "document_id": metadata["document_id"],
                "page": metadata["page"],
                "chunk_id": metadata["chunk_id"],
                "distance": distance,
            })

        return formatted_results
    
    def get_document(self, document_id):
        result = self.documents.get(
            ids=[document_id]
        )

        if len(result["ids"]) == 0:
            return None

        return {
            "document_id": result["ids"][0],
            "filename": result["documents"][0],
            "file_hash": result["metadatas"][0]["file_hash"],
            "total_pages": result["metadatas"][0]["total_pages"],
            "uploaded_at": result["metadatas"][0]["uploaded_at"]
        }
    
    def file_exists(self, file_hash: str) -> bool:
        try:
            result = self.documents.get(
                where={"file_hash": file_hash}
            )
            return len(result["ids"]) > 0
        
        except Exception:
            return False

   


    

        
    ## raw Chroma response


    # def search(self, query_embedding,top_k=3):

    #     results = self.collection.query(
    #         query_embeddings=[query_embedding],
    #         n_results=top_k
    #     )

    #     return results
    

    ## Cleaner Chroma response

    
    