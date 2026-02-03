FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH="/app/text_to_sql_engine/src"

EXPOSE 8000

# CMD ["python", "-m", "uvicorn", "text_to_sql_engine.src.ai_engine.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ls -R /app && python -m uvicorn ai_engine.api.server:app --host 0.0.0.0 --port 8000 --log-level debug
