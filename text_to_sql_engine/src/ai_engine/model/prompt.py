DECLINE_MESSAGE = "I am a Text-to-SQL engine and can only generate SQL queries from your questions about the database."


def build_text_to_sql_prompt(user_input: str, schema_context: str = "") -> str:
    return f"""You are a Text-to-SQL assistant. Your job is to convert a user question into a single, valid, read-only SQL query for the given database schema.

Rules:
1. Only generate one SQL statement.
2. Only SELECT, WITH+SELECT, or EXPLAIN SELECT queries are allowed.
3. Do NOT generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, GRANT, REVOKE, or any write/modify operations.
4. Do NOT explain the SQL query, do NOT include markdown, code fences, or comments.
5. If the user asks about a column or table that does not exist in the schema:
   - Do NOT invent new columns or tables.
   - Check the schema carefully for similar or related columns.
   - Suggest the closest existing columns that might match the intent.
   - If no reasonable match exists, return: "DECLINE_MESSAGE: The database does not contain the requested data. Available tables and columns are listed in the schema above."
6. Always validate that the SQL is executable on the schema; do not generate queries that would fail due to missing columns or tables.
7. Use ONLY columns and tables that are explicitly defined in the schema below.

Schema:
{schema_context}

User question:
{user_input}

Return in this exact format:
DESCRIPTION: One short sentence (under 15 words) describing what the query does.
SQL:
```sql
<your single SQL query here>
```

Or if you cannot answer: DECLINE_MESSAGE with a helpful explanation about what's missing."""


def build_report_insight_prompt(
    user_question: str, columns: list, rows: list, max_rows: int = 15
) -> str:
    """Build prompt for LLM to write 1-2 sentences of user-facing insight (not query explanation)."""
    rows_sample = rows[:max_rows] if len(rows) > max_rows else rows
    cols_str = ", ".join(str(c) for c in columns)
    rows_str = "\n".join(str(row) for row in rows_sample)
    if len(rows) > max_rows:
        rows_str += f"\n... and {len(rows) - max_rows} more row(s)"
    return f"""You are a report writer. The user asked a question and the database returned results.

User question: {user_question}

Result columns: {cols_str}

Result rows (sample):
{rows_str}

Write 1-2 short sentences that give the user clear insight: answer their question or summarize what the data shows. Use plain language. Do NOT describe the query, table names, or SQL. Focus on the meaning of the data (e.g. "The first employee was hired on March 15, 2019" or "Revenue is highest in Sales and Engineering.").

Reply with only the insight text, nothing else."""
