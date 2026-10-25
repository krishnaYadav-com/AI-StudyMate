import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


class LLMService:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash"
        )

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing. "
                "Please add it to your .env file."
            )

        self.client = genai.Client(
            api_key=api_key
        )

    def generate_response(self, prompt):

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        return response.text or ""

    def generate_response_stream(self, prompt):

        response_stream = (
            self.client.models.generate_content_stream(
                model=self.model,
                contents=prompt
            )
        )

        for chunk in response_stream:

            if chunk.text:
                yield chunk.text