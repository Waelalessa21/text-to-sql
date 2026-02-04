import os

llm_provider = "ollama"
ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip(
    "/"
)
ollama_model = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")
ollama_timeout = int(os.environ.get("OLLAMA_TIMEOUT", "600"))
ollama_temp = float(os.environ.get("OLLAMA_TEMP", "0.3"))
