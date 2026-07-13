from google import genai
from app.config import GEMINI_API_KEY


class QueryExpander:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def expand(self, query_text: str) -> list[str]:
        prompt = f"""
                    You are an AI assistant that improves search queries for a Retrieval-Augmented Generation (RAG) system.

                    Given a user's question, generate exactly 3 alternative search queries that preserve the original meaning while using different wording, synonyms, and related terminology.

                    Rules:
                    - Preserve the user's intent.
                    - Do not answer the question.
                    - Return exactly 3 queries.
                    - One query per line.
                    - Do not number the queries.
                    - Do not include explanations.
                    - Include the original query if it is already well-formed.

                    User Query:
                    {query_text}
                """

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )

            if not response.text:
                raise ValueError("Empty response received from Gemini.")

            queries = [
                q.strip()
                for q in response.text.splitlines()
                if q.strip()
            ]

            return queries

        except Exception as e:
            print(f"Query expansion failed: {e}")
            # Fallback to original query
            return [query_text]