import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is missing from your .env file."
    )

client = genai.Client(
    api_key=api_key
)

print("Fetching available Gemini models...\n")

try:

    models = client.models.list()

    for model in models:

        supported_actions = getattr(
            model,
            "supported_actions",
            []
        )

        if "generateContent" in supported_actions:

            print(
                "Model:",
                model.name
            )

            print(
                "Display name:",
                getattr(
                    model,
                    "display_name",
                    "Not available"
                )
            )

            print("-" * 50)

except Exception as error:

    print("Unable to list models.")

    print(
        type(error).__name__,
        error
    )