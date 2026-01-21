# db management module

from sqlalchemy import create_engine, inspect, text
from ..config.settings import settings

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)

    def get_schema(self):
        """retrieve and return the database schema information"""
        inspector = inspect(self.engine)
        schema_info = []
        
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            col_names = [f"{c['name']} ({c['type']})" for c in columns]
            schema_info.append(f"Table {table_name}: {', '.join(col_names)}")
        
        return "\n".join(schema_info)

    def execute_query(self, sql: str):
        """execute a given SQL query and return the results"""
        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            return result.keys(), result.fetchall()