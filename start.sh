#!/bin/bash
ollama serve > /dev/null 2>&1 &
sleep 10
ollama pull qwen2.5-coder:7b
PORT="${PORT:-8000}"
python -m uvicorn ai_engine.api.server:app --host 0.0.0.0 --port "$PORT"