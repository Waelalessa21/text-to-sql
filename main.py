import sys
from pathlib import Path

# BASE_DIR = Path(__file__).resolve().parent

# SRC_PATH = BASE_DIR / "text_to_sql_engine" / "src"

# if str(SRC_PATH) not in sys.path:
#     sys.path.insert(0, str(SRC_PATH))



from text_to_sql_engine.src.ai_engine.core.text_to_sql import TextToSQLEngine
from tabulate import tabulate

def main():
    print("🛸 Initializing System on NVIDIA GPU...")
    engine = TextToSQLEngine()
    print("✅ Ready for questions!")

    while True:
        question = input("\n[❓] USER: ")
        if question.lower() in ['exit', 'q', 'quit']: break
        
        try:
            sql, cols, rows = engine.process_query(question)
            print(f"\n🤖 SQL Generated: {sql}")
            print(tabulate(rows, headers=cols, tablefmt="psql"))
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()