from app.rag.embedding import EmbeddingService
from app.rag.vector_store import VectorStore
from app.rag.prompt_builder import build_prompt
from app.rag.generator import Generator


class RAGService:

    def __init__(self):

        self.embedding = EmbeddingService()

        self.vector_db = VectorStore()

        self.generator = Generator()

    def ask(self, question):

        query_embedding = self.embedding.embed([question])[0]

        results = self.vector_db.search(query_embedding)

        contexts = [

            item["text"]

            for item in results

        ]

        prompt = build_prompt(question,contexts)

        answer = self.generator.generate(prompt)

        return answer