# loads and initializes the SQL language model so it can be reused across the application.


import os
import ctypes
from llama_cpp import Llama
from huggingface_hub import hf_hub_download
from ..config.settings import settings

def load_ai_model():
    if os.path.exists(settings.CUDA_PATH):
        os.add_dll_directory(settings.CUDA_PATH)
    
    model_path = hf_hub_download(
        repo_id=settings.MODEL_REPO, 
        filename=settings.MODEL_FILE
    )
    
    return Llama(
        model_path=model_path,
        n_ctx=2048,
        n_gpu_layers=-1, # run on GPU
        verbose=False
    )