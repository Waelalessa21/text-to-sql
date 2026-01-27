import sys
from pathlib import Path

import pandas as pd
import streamlit as st

src = Path(__file__).resolve().parents[2]
if str(src) not in sys.path:
    sys.path.insert(0, str(src))

from ai_engine.core.database_manager import DatabaseManager
from ai_engine.core.text_to_sql import run as text_to_sql_run
from ai_engine.model.prompt import DECLINE_MESSAGE

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DB_PATH = PROJECT_ROOT / "data" / "company_data.db"
DB_URL = f"sqlite:///{DB_PATH}"


def run_ui():
    st.set_page_config(page_title="Text-to-SQL", layout="centered")
    st.title("Text-to-SQL Engine")

    db = st.cache_resource(lambda: DatabaseManager(DB_URL))()

    show_db = st.checkbox("Show DB", value=False)
    if show_db:
        schema = db.get_schema_text()
        st.subheader("Database schema")
        st.code(schema, language="text")

    user_input = st.text_area("Enter your question", placeholder="e.g. How many employees? List all departments.")
    send = st.button("Send to AI")

    if send and user_input.strip():
        with st.spinner("Querying..."):
            sql_or_decline, results, err = text_to_sql_run(user_input.strip(), db)

        if DECLINE_MESSAGE in sql_or_decline or sql_or_decline.strip() == DECLINE_MESSAGE:
            st.info(sql_or_decline)
        else:
            st.subheader("SQL")
            st.code(sql_or_decline, language="sql")
            if err:
                st.error(f"Execution failed: {err}")

        if results is not None:
            cols, rows = results
            df = pd.DataFrame(rows, columns=cols)
            st.subheader("Results")
            st.dataframe(df, use_container_width=True)
    elif send and not user_input.strip():
        st.warning("Enter a question first.")


if __name__ == "__main__":
    run_ui()
