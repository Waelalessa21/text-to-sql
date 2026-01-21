# The process of converting a natural language question into a valid SQL query that can be executed on a database.

from ..model.loader import load_ai_model
from ..model.prompt import SQL_PROMPT_TEMPLATE
from .database_manager import DatabaseManager
import re

class TextToSQLEngine:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.llm = load_ai_model()

    def process_query(self, user_text: str):
        # 1. get db Schema
        schema = self.db_manager.get_schema()
        
        # 2. generate SQL
        full_prompt = SQL_PROMPT_TEMPLATE.format(schema=schema, question=user_text)
        response = self.llm(full_prompt, max_tokens=250, stop=["<|im_end|>"])
        
        raw_sql = response["choices"][0]["text"].strip()
        # clean the respone
        clean_sql = re.sub(r"```sql|```", "", raw_sql).strip()
        
        # 3. execute SQL
        cols, rows = self.db_manager.execute_query(clean_sql)
        return clean_sql, cols, rows