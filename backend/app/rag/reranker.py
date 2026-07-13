from sentence_transformers import CrossEncoder


class Reranker:

    def __init__(self):
        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )
    
    def rerank(self, query_text, results, top_k=3):
        # Prepare the input for the CrossEncoder
        pairs = [(query_text, result["text"]) for result in results]

        # Get the scores from the CrossEncoder
        scores = self.model.predict(pairs)

        # Combine the results with their corresponding scores
        scored_results = [
            {**result, "rerank_score": float(score)} for result, score in zip(results, scores)
        ]

        # Sort the results based on the scores in descending order
        reranked_results = sorted(scored_results, key=lambda x: x["rerank_score"], reverse=True)

        return reranked_results[:top_k]
