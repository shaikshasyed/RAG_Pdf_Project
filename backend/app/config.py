from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SIMILARITY_THRESHOLD = 0.75
RETRIEVE_TOP_K = 10
FINAL_TOP_K = 3