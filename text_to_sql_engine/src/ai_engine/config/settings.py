# configurable values (model, limits, retries, environment settings)

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MODEL_REPO: str = "Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF"
    MODEL_FILE: str = "qwen2.5-coder-1.5b-instruct-q8_0.gguf"
    
    # postgresql://user:pass@host:5432/dbname TODO
    DATABASE_URL: str = "sqlite:///./company_data.db" 
    
    CUDA_PATH: str = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4\bin"

settings = Settings()