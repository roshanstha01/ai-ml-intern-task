#Ollama

from typing import List, Dict

import ollama


class OllamaService:
    def __init__(self, model_name: str = "llama3") -> None:
        self.model_name = model_name

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        response = ollama.chat(
            model=self.model_name,
            messages=messages,
        )
        return response["message"]["content"]