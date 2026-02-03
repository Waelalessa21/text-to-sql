import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

current_file = Path(__file__).resolve()
src_path = current_file.parent.parent.parent
import sys

sys.path.insert(0, str(src_path))

from ai_engine.core.database_manager import DatabaseManager
from ai_engine.core.plot_generator import PlotGenerator
from ai_engine.core.text_to_sql import run as text_to_sql_run

app = FastAPI()

_chart_cache: Dict[str, bytes] = {}


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
    visualize: Optional[bool] = None
    plot_type: Optional[str] = None


DEFAULT_DB_PATH = "sqlite:///./data/company_data.db"


@app.get("/chart/{chart_id}", response_class=Response)
async def get_chart(chart_id: str):
    """Serve a previously generated chart image by ID."""
    if chart_id not in _chart_cache:
        raise HTTPException(status_code=404, detail="Chart not found or expired.")
    return Response(content=_chart_cache[chart_id], media_type="image/png")


@app.post("/ask")
async def ask_ai(http_request: Request, request: QueryRequest):
    if request.connection_details and "url" in request.connection_details:
        db_url = request.connection_details["url"]
    else:
        db_url = DEFAULT_DB_PATH

    try:
        db_manager = DatabaseManager(db_url)

        full_prompt = f"Context: {request.context}\n\nQuestion: {request.user_prompt}"

        sql, results, err, description = text_to_sql_run(full_prompt, db_manager)

        if err:
            return {
                "status": "error",
                "error": err,
                "generated_sql": sql,
                "sql_description": description,
            }

        payload: Dict[str, Any] = {
            "status": "success",
            "generated_sql": sql,
            "sql_description": description,
            "results": results,
        }

        if request.visualize and results is not None:
            cols, rows = results
            if rows and cols:
                plot_gen = PlotGenerator(use_plotly=True)
                png_bytes, plot_err = plot_gen.get_figure_as_png(
                    request.user_prompt, cols, rows, plot_type=request.plot_type
                )
                if png_bytes is not None:
                    chart_id = str(uuid.uuid4())
                    _chart_cache[chart_id] = png_bytes
                    base = str(http_request.base_url).rstrip("/")
                    payload["image_url"] = f"{base}/chart/{chart_id}"
                else:
                    payload["image_url"] = None
                    payload["visualize_error"] = plot_err
            else:
                payload["image_url"] = None
        else:
            payload["image_url"] = None

        return payload

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database connection error: {str(e)}"
        )
