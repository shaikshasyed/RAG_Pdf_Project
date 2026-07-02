from google import genai
from app.config import GEMINI_API_KEY


class EmbeddingService:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def embed(self, texts: list[str]):
        embeddings = []

        for text in texts:
            response = self.client.models.embed_content(
                model="gemini-embedding-001",
                contents=text,
            )

            embeddings.append(response.embeddings[0].values)

        return embeddings