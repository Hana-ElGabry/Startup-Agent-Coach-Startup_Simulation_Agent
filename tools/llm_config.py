"""Google Gemini API configuration and usage."""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))


def generate_text(prompt: str, model: str = "gemini-2.5-flash-lite") -> str:
    """Generate text using Gemini."""
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text

if __name__ == '__main__':
    result = generate_text("Write one sentence about Egyptian startups.") # tryhere
    print(result)
