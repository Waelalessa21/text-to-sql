from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ai_engine.core.sql_validator import SqlPolicyValidator
from ai_engine.model.loader import ollama_response
from ai_engine.model.prompt import DECLINE_MESSAGE, build_text_to_sql_prompt

if TYPE_CHECKING:
    from ai_engine.core.database_manager import DatabaseManager


def _extract_sql(raw: str) -> str:
    s = raw.strip()
    markdown_match = re.search(r"```(?:sql)?\s*([\s\S]*?)```", s)
    if markdown_match:
        return markdown_match.group(1).strip()
    return s


def run(
    user_input: str, db_manager: "DatabaseManager"
) -> tuple[str, tuple[list, list] | None, str | None]:
    schema = db_manager.get_schema_text()
    prompt = build_text_to_sql_prompt(user_input, schema)
    response = ollama_response(prompt).strip()

    if "DECLINE_MESSAGE" in response or DECLINE_MESSAGE in response:
        return response, None, None

    sql = _extract_sql(response)
    if not sql:
        return response, None, "No SQL found in model output."

    validator = SqlPolicyValidator()
    is_valid, validation_message = validator.validate(sql)

    if not is_valid:
        return sql, None, validation_message

    try:
        cols, rows = db_manager.execute_query(sql)
        return sql, (cols, rows), None
    except Exception as e:
        return sql, None, str(e)
