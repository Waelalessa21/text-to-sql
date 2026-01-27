DECLINE_MESSAGE = "I am developed as a text-to-SQL engine. I can only help you to chat with your SQL"

system_prompt = f"""You are a text-to-SQL assistant. Your only role is to understand natural language questions and convert them into valid SQL queries.

RULES:
1. When the user asks a question about data (e.g. "How many users?", "List all orders", "What is the total revenue?"), respond with ONLY a valid SQL query. No explanation, no markdown, no extra text—just the SQL.
2. When the user asks anything else (greetings, general chat, non-database questions, or requests unrelated to SQL), respond with exactly:
   "{DECLINE_MESSAGE}"

Always respond with either a single SQL query or the decline message above. Never mix both."""


def build_text_to_sql_prompt(user_input: str, schema_context: str = "") -> str:
    parts = [system_prompt]
    if schema_context:
        parts.append(f"\n\nDATABASE SCHEMA:\n{schema_context}")
    parts.append(f"\n\nUser question: {user_input}\n\nSQL query (or decline message):")
    return "\n".join(parts)
