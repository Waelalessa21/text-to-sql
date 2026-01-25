db_key = 'hIf6jHu8L92WAdaO'
db_connection_string = f"postgresql://postgres:{db_key}@db.zgxvqzmenptjfrqulewv.supabase.co:5432/postgres"

from text_to_sql_engine.src.ai_engine.core.get_db_schema import get_db_schema

def main():
    print("Hello from text-to-sql!")
    
    


if __name__ == "__main__":
    main()
