import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

current_file = Path(__file__).resolve()
src_path = current_file.parent.parent.parent
sys.path.insert(0, str(src_path))

from ai_engine.core.database_manager import DatabaseManager
from ai_engine.core.plot_generator import PlotGenerator
from ai_engine.core.report_insight import get_report_insight
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
    generate_report: Optional[bool] = (
        None  # when True, include report details (title, summary, executed_query, etc.)
    )


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

        try:
            sql, results, err, description = text_to_sql_run(full_prompt, db_manager)
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout) as e:
            logger.warning("LLM (Ollama) request failed: %s", e)
            raise HTTPException(
                status_code=503,
                detail=f"LLM unavailable. Ensure Ollama is running and the model is loaded. ({e!s})",
            )

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

        if request.generate_report:
            try:
                cols = results[0] if results and len(results) >= 1 else []
                rows_list = results[1] if results and len(results) == 2 else []
                row_count = len(rows_list)
                insight = get_report_insight(request.user_prompt, cols, rows_list)
                payload["report"] = {
                    "title": (
                        (request.user_prompt[:80] + "…")
                        if len(request.user_prompt) > 80
                        else request.user_prompt
                    ),
                    "summary": insight or description or "Query executed successfully.",
                    "executed_query": sql,
                    "row_count": row_count,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                }
            except Exception as report_err:
                _rows = results[1] if results and len(results) == 2 else []
                payload["report"] = {
                    "title": request.user_prompt[:80]
                    + ("…" if len(request.user_prompt) > 80 else ""),
                    "summary": description or "Query executed successfully.",
                    "executed_query": sql,
                    "row_count": len(_rows),
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "report_error": str(report_err),
                }
        else:
            payload["report"] = None

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

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("POST /ask failed")
        raise HTTPException(status_code=500, detail=str(e))
