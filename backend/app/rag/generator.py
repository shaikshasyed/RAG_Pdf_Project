from google import genai
from app.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


class Generator:

    def generate(self, prompt: str):

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text
    
    def generate_stream(self, prompt):

        stream = client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        for chunk in stream:
            if chunk.text:
                yield chunk.text