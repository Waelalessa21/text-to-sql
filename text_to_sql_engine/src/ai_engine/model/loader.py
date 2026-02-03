from typing import Any, Dict

import requests

from ai_engine.config.settings import (
    ollama_base_url,
    ollama_model,
    ollama_temp,
    ollama_timeout,
)


def ollama_response(prompt: str) -> str:
    response = requests.post(
        f"{ollama_base_url}/api/generate",
        json={
            "model": ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": ollama_temp},
        },
        timeout=ollama_timeout,
    )

    response.raise_for_status()

    data: Dict[str, Any] = response.json()
    result: str = str(data.get("response", "")).strip()
    return result
