import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def init_gemini():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not found in environment")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-3-flash-preview")
    


