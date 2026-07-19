
from app.rag.embedding import EmbeddingService
import numpy as np

class ContextCompressor:
    def __init__(self, max_tokens = 2000,similarity_threshold=0.90,):
        self.max_tokens = max_tokens
        self.similaity_threshold = similarity_threshold
        self.embedding_service = EmbeddingService()
        

    def apply_token_budget(self, results):
        original_tokens = sum( len(result["text"].split()) for result in results )

        compressed_results = []
        running_tokens  = 0
        for result in results:
            estimate_tokens = len(result["text"].split())

            if estimate_tokens + running_tokens > 2000:
                return
            
            compressed_results.append(result)
            running_tokens += estimate_tokens

        compressed_tokens = running_tokens

        metrics = {
            "original_chunks": len(results),
            "compressed_chunks": len(compressed_results),
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "saved_tokens": original_tokens - compressed_tokens,
        }

        compression_ratio = (
                compressed_tokens / original_tokens
                if original_tokens > 0
                else 0
            )
        
        metrics["compression_ratio"] = round(compression_ratio, 2)

        return compressed_results, metrics
    
    def _cosine_similarity(self, vec1, vec2):
        return np.dot(vec1, vec2) / (
                    np.linalg.norm(vec1) * np.linalg.norm(vec2)
                )
    
    def remove_redundant_chunks(self, results):
        if not results:
            return []

        embeddings = [result["embedding"] for result in results]

        filtered_results = []
        filtered_embeddings = []

        for result, embedding in zip(results, embeddings):
            is_duplicate = False

            for kept_embedding in filtered_embeddings:
                similarity = self._cosine_similarity(embedding, kept_embedding)

                if similarity >= self.similaity_threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                filtered_results.append(result)
                filtered_embeddings.append(embedding)

        return filtered_results
    
    def compress(self, results):
        results = self.remove_redundant_chunks(results)
        results, metrics = self.apply_token_budget(results)

        return results, metrics





