import sys
from pathlib import Path
from text_to_sql_engine.src.ai_engine.config.config_manager import ConfigManager
from text_to_sql_engine.src.ai_engine.core.database_manager import DatabaseManager
from text_to_sql_engine.src.ai_engine.core.text_to_sql import TextToSQLEngine


def select_database(config):
    dbs = config.config_data.get("databases", [])
    
    if not dbs:
        print("❌ No databases found in config!")
        sys.exit(1)
    
    # Auto-choose if only one exists
    if len(dbs) == 1:
        selected_db = dbs[0]
    else:
        print("\n--- Available Databases ---")
        for i, db in enumerate(dbs, 1):
            print(f"{i}. {db['name']} ({db['type']})")
        
        choice = int(input(f"\nSelect a database (1-{len(dbs)}): "))
        selected_db = dbs[choice - 1]
    
    config.switch_active_db(selected_db['id'])
    return selected_db

def main():
    config = ConfigManager()
    
    while True:
        # Step 1: Select Database
        db_info = select_database(config)
        print(f"\n✅ Connected to: {db_info['name']}")
        
        db_manager = DatabaseManager(db_info['url'])
        engine = None # Lazy load engine only when needed

        while True:
            print(f"\n--- Main Menu ({db_info['name']}) ---")
            print("1. Enter Question Loop")
            print("2. Preview Schema / DB Info")
            print("3. Change Database")
            print("4. Add New Database (Coming Soon)")
            print("q. Exit Program")
            
            choice = input("\nSelect an option: ").strip().lower()

            if choice == '1':
                # Question Loop
                if engine is None:
                    print("🧠 Loading AI Engine... please wait.")
                    engine = TextToSQLEngine(db_manager)
                
                while True:
                    query = input("\n[❓] Ask a question (or type 'back' to return): ")
                    if query.lower() == 'back':
                        break
                    
                    try:
                        sql, cols, rows = engine.process_query(query)
                        print(f"\n🤖 Generated SQL:\n{sql}")
                        print(f"📊 Results: {rows}")
                    except Exception as e:
                        print(f"⚠️ Error: {e}")

            elif choice == '2':
                print("\n--- Database Schema ---")
                print(db_manager.get_schema_text())
                input("\nPress Enter to return...")

            elif choice == '3':
                print("🔄 Switching database...")
                break # Breaks inner loop to trigger DB selection again

            elif choice == '4':
                print("\n🏗️ Feature coming soon: Implementation of dynamic JSON updates.")
            
            elif choice == 'q':
                print("Goodbye!")
                sys.exit(0)
            else:
                print("Invalid choice, try again.")

if __name__ == "__main__":
    main()