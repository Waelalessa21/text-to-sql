#!/bin/bash
ollama serve > /dev/null 2>&1 &
sleep 10
ollama pull -q qwen2.5-coder:7b
python -m uvicorn ai_engine.api.server:app --host 0.0.0.0 --port 8000