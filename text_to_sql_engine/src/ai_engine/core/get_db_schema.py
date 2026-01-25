import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).resolve().parents[4] / "data" / "company_data.db"

def get_schema(db_path=DB_FILE):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    schema_text = ""

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table_name in tables:
        table = table_name[0]
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        col_str = ", ".join([f"{col[1]} ({col[2]})" for col in columns])
        schema_text += f"Table {table}: {col_str}\n"

    conn.close()
    return schema_text

if __name__ == "__main__":
    schema = get_schema()
    print(schema)
