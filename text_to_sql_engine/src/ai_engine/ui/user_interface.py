import streamlit as st
import sqlite3
from pathlib import Path
import pandas as pd
import sys

try:
    from ..core.get_db_schema import get_schema
except ImportError:
    src_path = Path(__file__).resolve().parents[2]  
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    from ai_engine.core.get_db_schema import get_schema

DB_FILE = Path(__file__).resolve().parents[4] / "data" / "company_data.db"

def run_ui():
    st.title("Text to SQL Engine")

    if st.button("Show All Database Records"):
        conn = sqlite3.connect(DB_FILE)
        
        st.header("Database Records")
        tables = ["departments", "employees", "projects"]
        
        for table in tables:
            st.subheader(f"{table.capitalize()}")
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            st.dataframe(df, use_container_width=True)
            st.write("---")
        
        conn.close()
        
        st.header("Database Schema")
        schema = get_schema(DB_FILE)
        st.code(schema, language="text")

if __name__ == "__main__":
    run_ui()
