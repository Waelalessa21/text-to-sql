"""Generate user-facing report insight from query results (LLM)."""

from typing import List, Optional

from ai_engine.model.loader import ollama_response
from ai_engine.model.prompt import build_report_insight_prompt


def get_report_insight(
    user_prompt: str,
    columns: List[str],
    rows: List[List],
    max_rows: int = 15,
) -> Optional[str]:
    """Ask the model for 1-2 sentences of insight (answer / what the data shows). Returns None on failure."""
    if not rows or not columns:
        return None
    try:
        prompt = build_report_insight_prompt(
            user_prompt, columns, rows, max_rows=max_rows
        )
        insight = ollama_response(prompt).strip()
        return insight if insight else None
    except Exception:
        return None
