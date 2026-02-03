FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    zstd \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/text_to_sql_engine/src
ENV OLLAMA_HOST=0.0.0.0

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]