# The process of converting a natural language question into a valid SQL query that can be executed on a database.

from ..model.loader import load_ai_model
from ..model.prompt import SQL_PROMPT_TEMPLATE
from ..core.database_manager import DatabaseManager
import re


class TextToSQLEngine:
    def __init__(self, db_manager: str):
        self.db_manager = db_manager
        self.llm = load_ai_model()
        
    def process_query(self, user_text: str, custom_schema: str = None):
        # إذا كانت السكيما مخصصة (نصية) نستخدمها مباشرة، وإلا نسحبها من القاعدة
        schema = custom_schema if custom_schema else self.db_manager.get_schema_text()
        
        full_prompt = SQL_PROMPT_TEMPLATE.format(schema=schema, question=user_text)
        
        # استدعاء الموديل
        response = self.llm(full_prompt, max_tokens=250, stop=["<|im_end|>"])
        raw_sql = response["choices"][0]["text"].strip()
        clean_sql = re.sub(r"```sql|```", "", raw_sql).strip()
        
        # في حالة السكيما المخصصة، لا يوجد تنفيذ (Execution)
        if custom_schema:
            return clean_sql, [], []
            
        cols, rows = self.db_manager.execute_query(clean_sql)
        return clean_sql, cols, rows
    
    # def process_query(self, user_text: str):
    #     schema = self.db_manager.get_schema_text() 
        
    #     full_prompt = SQL_PROMPT_TEMPLATE.format(
    #         schema=schema, 
    #         question=user_text
    #     )
    #     response = self.llm(full_prompt, max_tokens=250, stop=["<|im_end|>"])
        
    #     raw_sql = response["choices"][0]["text"].strip()
    #     # clean the respone
    #     clean_sql = re.sub(r"```sql|```", "", raw_sql).strip()
        
    #     # 3. execute SQL
    #     cols, rows = self.db_manager.execute_query(clean_sql)
    #     return clean_sql, cols, rows