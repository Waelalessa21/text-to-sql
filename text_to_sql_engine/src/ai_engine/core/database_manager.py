import sqlalchemy
from sqlalchemy import create_engine, MetaData, inspect, text
from sqlalchemy.engine import Engine
from typing import List, Tuple, Dict

class DatabaseManager:
    def __init__(self, connection_string: str):

        self.connection_string = connection_string
        
        self.engine: Engine = create_engine(
            connection_string, 
            pool_pre_ping=True
        )
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)

    def get_schema_text(self) -> str:

        inspector = inspect(self.engine)
        schema_parts = []

        for table_name in inspector.get_table_names():
            table_info = f"Table: {table_name}\nColumns:\n"
            
            columns = inspector.get_columns(table_name)
            for col in columns:
                col_type = str(col['type'])
                col_name = col['name']
                table_info += f"  - {col_name} ({col_type})\n"
            
            fks = inspector.get_foreign_keys(table_name)
            for fk in fks:
                referred_table = fk['referred_table']
                referred_cols = fk['referred_columns']
                constrained_cols = fk['constrained_columns']
                table_info += f"  * Foreign Key: {constrained_cols} -> {referred_table}({referred_cols})\n"
            
            schema_parts.append(table_info)
        
        return "\n".join(schema_parts)

    def execute_query(self, sql_query: str) -> Tuple[List[str], List[Dict]]:

        with self.engine.connect() as connection:
            result = connection.execute(text(sql_query))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return columns, rows