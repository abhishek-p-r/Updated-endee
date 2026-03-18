# backend/utils/openai_client.py

import os

class OpenAIClient:
    def __init__(self):
        # You can later add API key here
        self.api_key = os.getenv("OPENAI_API_KEY", "demo-key")

    def get_response(self, prompt: str):
        # Temporary dummy response (replace later with real OpenAI call)
        return {
            "response": f"Echo: {prompt}"
        }


def get_openai_client():
    return OpenAIClient()