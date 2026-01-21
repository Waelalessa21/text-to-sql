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