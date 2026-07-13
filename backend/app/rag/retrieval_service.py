from app.rag.vector_store import VectorStore
from app.rag.bm25_retriever import BM25Retriever

class RetrievalService:

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.bm25_retriever = BM25Retriever()
        chunks = self.vector_store.get_all_chunks()

        if chunks:
            self.bm25_retriever.index(chunks)
    

    # Method for Automatic BM25 refresh after uploads 
    def refresh_index(self):
        chunks = self.vector_store.get_all_chunks()

        if chunks:
            self.bm25_retriever.index(chunks)


    def deduplicate_results(self, results):
        unique_results = []
        seen = set()

        for result in results:
            key = (result["document_id"], result["chunk_id"])

            if key not in seen:
                seen.add(key)
                unique_results.append(result)

        return unique_results

    
    def retrieve(self, query_text, query_embedding, document_id = None,retrieve_top_k=10,):
        vector_results = self.vector_store.search(query_embedding = query_embedding, document_id=document_id, top_k=retrieve_top_k)
        
        bm25_results = self.bm25_retriever.search(query=query_text, document_id=document_id, top_k=retrieve_top_k)

        merged = vector_results + bm25_results

        results = self.deduplicate_results(merged) 
        return results
    
    
            




        