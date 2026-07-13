from app.config import RETRIEVE_TOP_K



class MultiQueryRetriever:
    
    def __init__(self, retrieval_service, embedding_service):

        self.retrieval_service = retrieval_service
        self.embedding_service = embedding_service

    def retrieve(self, expanded_queries, document_id = None):
        all_results = []

        for query in expanded_queries:
            query_embedding = self.embedding_service.embed([query])[0]


            results = self.retrieval_service.retrieve(
                query_text=query,
                query_embedding=query_embedding,
                document_id=document_id,
                retrieve_top_k=RETRIEVE_TOP_K,
            )
            all_results.extend(results)

        #remove duplicate results using the method in the retrievalService
        unique_results = self.retrieval_service.deduplicate_results(all_results)
    
        return unique_results

