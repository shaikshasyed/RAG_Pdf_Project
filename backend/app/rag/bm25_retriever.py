from rank_bm25 import BM25Okapi


class BM25Retriever:

    def __init__(self):
        self.bm25 = None
        self.documents = []
    
    def index(self, chunks):

        self.documents = chunks

        tokenized_chunks = [chunk["text"].lower().split() for chunk in chunks]

        self.bm25 = BM25Okapi(tokenized_chunks)
    
    def search(self, query,document_id=None ,top_k=3):

        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        indices = list(range(len(scores)))

        ranked_indices = sorted(indices, key=lambda i: scores[i], reverse=True)

        top_k_indices = ranked_indices[:top_k]

        results = []
        for idx in top_k_indices:
            chunk = self.documents[idx]
            if document_id and chunk["document_id"] != document_id:
                continue

            results.append({
                "document_id": chunk["document_id"],
                "chunk_id": chunk["chunk_id"],
                "page": chunk["page"],
                "text": chunk["text"],
                "score": scores[idx],
                "retrieval_type": "bm25"
            })


            
        
        return results
            



        