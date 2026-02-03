#!/bin/bash
set -e

PORT="${PORT:-8000}"

python -m uvicorn ai_engine.api.server:app --host 0.0.0.0 --port "$PORT" &
UVICORN_PID=$!

if command -v ollama >/dev/null 2>&1; then
  ollama serve > /dev/null 2>&1 &
  sleep 3
  (ollama pull qwen2.5-coder:7b > /dev/null 2>&1) &
fi

wait $UVICORN_PID