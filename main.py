import sys
from pathlib import Path
from text_to_sql_engine.src.ai_engine.config.config_manager import ConfigManager
from text_to_sql_engine.src.ai_engine.core.database_manager import DatabaseManager
from text_to_sql_engine.src.ai_engine.core.text_to_sql import TextToSQLEngine

BASE_DIR = Path(__file__).resolve().parent
SRC_PATH = BASE_DIR / "text_to_sql_engine" / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

def main():
    config = ConfigManager()
    db_info = config.get_active_db_info()
    
    print(f"🚀 Connecting to {db_info['name']}...")
    db_manager = DatabaseManager(db_info['url'])
    engine = TextToSQLEngine(db_manager)
    
    question = input("\nUSER QUESTION: ")
    generated_sql, cols, rows = engine.process_query(question)

    print(f"🤖 Generated SQL: {generated_sql}")

    print(f"📊 Results:")
    for row in rows:
        print(row)

if __name__ == "__main__":
    main()