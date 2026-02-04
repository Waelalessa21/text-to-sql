import sys
from pathlib import Path
from typing import Optional

import pandas as pd  # type: ignore
import streamlit as st  # type: ignore

src = Path(__file__).resolve().parents[2]
if str(src) not in sys.path:
    sys.path.insert(0, str(src))

from ai_engine.core.database_manager import DatabaseManager  # type: ignore
from ai_engine.core.plot_generator import PlotGenerator  # type: ignore
from ai_engine.core.text_to_sql import run as text_to_sql_run  # type: ignore
from ai_engine.model.prompt import DECLINE_MESSAGE  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parents[4]
LOCAL_DB_URL = f"sqlite:///{PROJECT_ROOT / 'data' / 'company_data.db'}"


@st.cache_resource
def _get_db(connection_string: str):
    return DatabaseManager(connection_string)


def _test_connection(
    connection_string: str,
) -> tuple[bool, str, Optional[DatabaseManager]]:
    try:
        db = DatabaseManager(connection_string)
        schema = db.get_schema_text()
        tables = len([line for line in schema.split("\n") if line.startswith("Table:")])
        return True, f"Connected! Found {tables} table(s)", db
    except Exception as e:
        return False, f"Connection failed: {str(e)}", None


def run_ui():
    st.set_page_config(page_title="Text-to-SQL", layout="centered")
    st.title("Text-to-SQL Engine")

    if "db_connection" not in st.session_state:
        st.session_state.db_connection = LOCAL_DB_URL
        st.session_state.db_name = "Local SQLite"

    with st.sidebar:
        st.header("Database Connection")

        db_type = st.selectbox(
            "Select Database Type",
            ["SQLite (Local)", "PostgreSQL", "MySQL"],
            key="db_type_select",
        )

        if db_type == "SQLite (Local)":
            st.info("Using local database: company_data.db")
            connection_string = LOCAL_DB_URL

        elif db_type == "PostgreSQL":
            st.subheader("PostgreSQL Connection")

            with st.form("postgres_form"):
                host = st.text_input(
                    "Host", value="localhost", placeholder="localhost or IP"
                )
                port = st.text_input("Port", value="5432")
                database = st.text_input("Database Name", placeholder="mydb")
                username = st.text_input("Username", placeholder="postgres")
                password = st.text_input("Password", type="password")
                use_ssl = st.checkbox("Use SSL", value=True)

                submitted = st.form_submit_button("Connect")

                if submitted:
                    if all([host, port, database, username, password]):
                        ssl_param = "?sslmode=require" if use_ssl else ""
                        connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}{ssl_param}"

                        with st.spinner("Testing connection..."):
                            success, message, db_test = _test_connection(
                                connection_string
                            )

                        if success:
                            st.success(message.replace("✅", "").strip())
                            st.session_state.db_connection = connection_string
                            st.session_state.db_name = f"PostgreSQL: {database}"
                            st.rerun()
                        else:
                            st.error(message.replace("❌", "").strip())
                    else:
                        st.warning("Please fill in all fields")

            connection_string = st.session_state.db_connection

        else:  # MySQL
            st.subheader("MySQL Connection")

            with st.form("mysql_form"):
                host = st.text_input(
                    "Host", value="localhost", placeholder="localhost or IP"
                )
                port = st.text_input("Port", value="3306")
                database = st.text_input("Database Name", placeholder="mydb")
                username = st.text_input("Username", placeholder="root")
                password = st.text_input("Password", type="password")

                submitted = st.form_submit_button("Connect")

                if submitted:
                    if all([host, port, database, username, password]):
                        connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

                        with st.spinner("Testing connection..."):
                            success, message, db_test = _test_connection(
                                connection_string
                            )

                        if success:
                            st.success(message.replace("✅", "").strip())
                            st.session_state.db_connection = connection_string
                            st.session_state.db_name = f"MySQL: {database}"
                            st.rerun()
                        else:
                            st.error(message.replace("❌", "").strip())
                    else:
                        st.warning("Please fill in all fields")

            connection_string = st.session_state.db_connection

        st.divider()
        st.caption(f"**Connected to:** {st.session_state.db_name}")

    db = _get_db(connection_string)

    # Schema toggle
    show_schema = st.checkbox("Show schema", value=False)
    if show_schema:
        st.subheader("Database Schema")
        st.code(db.get_schema_text(), language="text")

    # User input
    user_input = st.text_area(
        "Ask a question about your data",
        placeholder="e.g. How many employees? List all departments. What is the average salary?",
        height=100,
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        send = st.button("Generate SQL & Run", type="primary", use_container_width=True)
    with col2:
        with_plot = st.checkbox("Visualize", value=False)

    plot_type = "Auto-detect"
    if with_plot:
        plot_type = st.selectbox(
            "Plot type",
            ["Auto-detect", "Bar", "Line", "Scatter", "Pie", "Histogram"],
            key="plot_type_select",
        )

    if send and user_input.strip():
        with st.spinner("Generating SQL query..."):
            sql_or_decline, results, err, description = text_to_sql_run(user_input.strip(), db)

        # Check if declined
        if (
            DECLINE_MESSAGE in sql_or_decline
            or sql_or_decline.strip() == DECLINE_MESSAGE
        ):
            st.info(sql_or_decline)
        else:
            # Show generated SQL
            st.subheader("Generated SQL")
            st.code(sql_or_decline, language="sql")

            if err:
                st.error(f"Execution failed: {err}")

            # Show results if available
            if results is not None:
                cols, rows = results
                df = pd.DataFrame(rows, columns=cols)
                st.subheader("Results")
                st.dataframe(df, use_container_width=True)
                st.caption(f"Found {len(rows)} row(s)")

                if with_plot and len(rows) > 0:
                    plot_gen = PlotGenerator(use_plotly=True)
                    if plot_type == "Auto-detect":
                        plot_request = user_input
                        selected_plot_type = None
                    else:
                        plot_request = user_input
                        selected_plot_type = plot_type.lower()

                    df_result, plot_code, plot_err = plot_gen.generate(
                        plot_request, cols, rows, plot_type=selected_plot_type
                    )

                    if plot_code:
                        st.subheader("Visualization")
                        try:
                            import plotly.express as px

                            # px is already imported and provided in exec context
                            exec_globals = {"df": df_result, "px": px}
                            exec(plot_code, exec_globals)
                            fig = exec_globals.get("fig")
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.warning("Plot figure was not created successfully.")
                        except ImportError as e:
                            st.error(
                                f"Plot generation failed: Missing dependency. Please ensure plotly is installed in your Python environment. Error: {str(e)}"
                            )
                            st.info(
                                "To fix: Activate your virtual environment and run: pip install plotly"
                            )
                        except Exception as e:
                            st.error(f"Plot generation failed: {str(e)}")
                    elif plot_err:
                        st.warning(f"Visualization: {plot_err}")
                    else:
                        st.warning(
                            "Could not generate visualization. Please try selecting a specific plot type."
                        )
    elif send and not user_input.strip():
        st.warning("Please enter a question first.")


if __name__ == "__main__":
    run_ui()
