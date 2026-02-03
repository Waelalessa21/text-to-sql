from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import sys
from pathlib import Path


current_file = Path(__file__).resolve()
src_path = current_file.parent.parent.parent
sys.path.append(str(src_path))

from ai_engine.core.database_manager import DatabaseManager
from ai_engine.core.text_to_sql import run as text_to_sql_run

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "ok", "service": "text-to-sql"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    user_prompt: str
    context: Optional[str] = ""
    connection_details: Optional[Dict[str, Any]] = None


DEFAULT_DB_PATH = "sqlite:///./data/company_data.db"


@app.post("/ask")
async def ask_ai(request: QueryRequest):
    if request.connection_details and "url" in request.connection_details:
        db_url = request.connection_details["url"]
    else:
        db_url = DEFAULT_DB_PATH

    try:
        db_manager = DatabaseManager(db_url)

        full_prompt = f"Context: {request.context}\n\nQuestion: {request.user_prompt}"

        sql, results, err = text_to_sql_run(full_prompt, db_manager)

        if err:
            return {"status": "error", "error": err, "generated_sql": sql}

        return {"status": "success", "generated_sql": sql, "results": results}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database connection error: {str(e)}"
        )
