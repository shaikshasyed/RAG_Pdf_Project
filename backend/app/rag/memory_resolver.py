from google import genai
from app.config import GEMINI_API_KEY

class MemoryResolver:

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def resolve(self, query: str, history: list) -> str:
        if not history:
            return query

        history_text = "\n".join(
            f"{item['role']}: {item['content']}"
            for item in history
        )

        prompt = f"""
                    You are helping a Retrieval-Augmented Generation (RAG) system.

                    Given the conversation history and the user's latest question, rewrite the latest question into a complete standalone question.

                    Rules:

                    - Preserve the original meaning.
                    - Replace pronouns like "it", "they", "this", "that" with the correct subject.
                    - Do not answer the question.
                    - If the question is already standalone, return it unchanged.
                    - Return only the rewritten question.

                    Conversation:
                    {history_text}

                    Latest Question:
                    {query}
                """
        try:

            response = self.client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt
                        )

            
            return response.text.strip()

        except Exception:
            return query