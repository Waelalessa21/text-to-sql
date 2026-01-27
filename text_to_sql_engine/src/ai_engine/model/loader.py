import requests 
from ai_engine.config.settings import ollama_base_url, ollama_model, ollama_timeout, ollama_temp

def ollama_response(prompt: str) -> str:
    response = requests.post(
        f"{ollama_base_url}/api/generate",
        json={
            "model": ollama_model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=ollama_timeout,
    )

    response.raise_for_status()

    return response.json()["response"].strip()