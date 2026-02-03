from typing import List, Tuple

from sqlalchemy import MetaData, create_engine, inspect, text


class DatabaseManager:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string, pool_pre_ping=True)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)

    def get_schema_text(self) -> str:
        inspector = inspect(self.engine)
        schema_parts = []

        for table_name in inspector.get_table_names():
            table_info = f"Table: {table_name}\nColumns:\n"

            for col in inspector.get_columns(table_name):
                table_info += f"  - {col['name']} ({str(col['type'])})\n"

            for fk in inspector.get_foreign_keys(table_name):
                table_info += f"  * FK: {fk['constrained_columns']} -> {fk['referred_table']}({fk['referred_columns']})\n"

            schema_parts.append(table_info)

        return "\n".join(schema_parts)

    def execute_query(self, sql_query: str) -> Tuple[List[str], List[List]]:
        with self.engine.connect() as conn:
            result = conn.execute(text(sql_query))
            columns = list(result.keys())
            rows = [list(row) for row in result.fetchall()]
            return columns, rows
