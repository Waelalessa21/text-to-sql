import sys
from pathlib import Path

import pandas as pd  # type: ignore
import streamlit as st  # type: ignore

src = Path(__file__).resolve().parents[2]
if str(src) not in sys.path:
    sys.path.insert(0, str(src))

from ai_engine.config.config_manager import ConfigManager  # type: ignore
from ai_engine.config.database_types import SupportedDatabaseTypes  # type: ignore
from ai_engine.core.database_manager import DatabaseManager  # type: ignore
from ai_engine.core.firebase_manager import FirebaseManager  # type: ignore
from ai_engine.core.firebase_query import run_firebase_query  # type: ignore
from ai_engine.core.text_to_sql import run as text_to_sql_run  # type: ignore
from ai_engine.model.prompt import DECLINE_MESSAGE  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CONFIG_PATH = PROJECT_ROOT / "data" / "user_config.json"
LOCAL_DB_URL = f"sqlite:///{PROJECT_ROOT / 'data' / 'company_data.db'}"

LOCAL_KEY = "__local__"


def _get_config():
    if not CONFIG_PATH.exists():
        return None
    try:
        return ConfigManager(str(CONFIG_PATH))
    except Exception:
        return None


def _connection_options(config):
    options = [("Local (company_data.db)", LOCAL_KEY)]
    if config:
        for db in config.config_data.get("databases", []):
            options.append((db["name"], db["id"]))
        for fp in config.get_firebase_projects():
            options.append((f"Firebase: {fp['name']}", fp["id"]))
    return options


def _is_firebase(choice, config):
    if not config or choice == LOCAL_KEY:
        return False
    return config.get_firebase_project(choice) is not None


def _get_firebase_config(choice, config):
    if not config:
        return None
    return config.get_firebase_project(choice)


def _connection_string(choice, config):
    if choice == LOCAL_KEY:
        return LOCAL_DB_URL
    if config:
        for db in config.config_data.get("databases", []):
            if db["id"] == choice:
                return db["url"]
    return LOCAL_DB_URL


def _get_db(connection_string: str):
    return DatabaseManager(connection_string)


def _get_firebase(project_id: str, credentials_path: str, app_name: str):
    return FirebaseManager(project_id, credentials_path, app_name)


def run_ui():
    st.set_page_config(page_title="Text-to-SQL", layout="centered")
    st.title("Text-to-SQL Engine")

    config = _get_config()
    options = _connection_options(config)
    labels = [o[0] for o in options]
    keys = [o[1] for o in options]

    if "db_choice" not in st.session_state:
        st.session_state.db_choice = (
            config.config_data.get("active_db_key", LOCAL_KEY) if config else LOCAL_KEY
        )
        if st.session_state.db_choice not in keys:
            st.session_state.db_choice = LOCAL_KEY

    idx = (
        keys.index(st.session_state.db_choice)
        if st.session_state.db_choice in keys
        else 0
    )
    selected_label = st.selectbox(
        "Database", options=labels, index=idx, key="db_select"
    )
    selected_key = keys[labels.index(selected_label)]
    st.session_state.db_choice = selected_key
    if config and selected_key != LOCAL_KEY:
        config.switch_active_db(selected_key)

    with st.expander("Add external database"):
        add_name = st.text_input("Name", key="add_db_name", placeholder="My PostgreSQL")
        add_type = st.selectbox("Type", SupportedDatabaseTypes.all(), key="add_db_type")
        add_url = st.text_input(
            "Connection URL",
            key="add_db_url",
            placeholder=SupportedDatabaseTypes.placeholder_for(add_type),
        )
        if st.button("Add and use"):
            if add_name.strip() and add_url.strip():
                if config:
                    db_id = add_name.strip().lower().replace(" ", "_").replace("-", "_")
                    config.add_database(
                        db_id, add_name.strip(), add_type, add_url.strip()
                    )
                    st.session_state.db_choice = db_id
                    st.rerun()
                else:
                    st.warning(
                        "Config not found. Add data/user_config.json to add connections."
                    )
            else:
                st.warning("Name and URL required.")

    with st.expander("Connect Firebase"):
        fb_name = st.text_input("Name", key="fb_name", placeholder="My Firebase App")
        fb_project_id = st.text_input(
            "Project ID", key="fb_project_id", placeholder="my-project-id"
        )
        fb_credentials = st.text_input(
            "Credentials path",
            key="fb_credentials",
            placeholder="path/to/serviceAccountKey.json",
        )
        if st.button("Add Firebase and use"):
            if fb_name.strip() and fb_project_id.strip() and fb_credentials.strip():
                if config:
                    fb_id = "fb_" + fb_name.strip().lower().replace(" ", "_").replace(
                        "-", "_"
                    )
                    config.add_firebase_project(
                        fb_id,
                        fb_name.strip(),
                        fb_project_id.strip(),
                        fb_credentials.strip(),
                    )
                    st.session_state.db_choice = fb_id
                    st.rerun()
                else:
                    st.warning(
                        "Config not found. Add data/user_config.json to add connections."
                    )
            else:
                st.warning("Name, Project ID and Credentials path required.")

    is_firebase = _is_firebase(st.session_state.db_choice, config)
    if is_firebase:
        fb_config = _get_firebase_config(st.session_state.db_choice, config)
        cred_path = fb_config["credentials_path"]
        if not Path(cred_path).is_absolute():
            cred_path = str(PROJECT_ROOT / cred_path)
        try:
            firebase_mgr = st.cache_resource(_get_firebase)(
                fb_config["project_id"], cred_path, fb_config["id"]
            )
        except RuntimeError as e:
            st.error(
                str(e)
                + " Use the same Python that runs Streamlit (e.g. `python3.13 -m pip install firebase-admin`)."
            )
            firebase_mgr = None
        if firebase_mgr is not None:
            show_schema = st.checkbox("Show schema", value=False)
            if show_schema:
                st.subheader("Schema")
                try:
                    st.code(firebase_mgr.get_schema_text(), language="text")
                except Exception as e:
                    st.error(str(e))
        user_input = st.text_area(
            "Question",
            placeholder="e.g. Show users, List documents in orders.",
        )
        send = st.button("Run")
        if send and user_input.strip() and firebase_mgr is not None:
            with st.spinner("Querying Firestore..."):
                coll_name, results, err = run_firebase_query(
                    user_input.strip(), firebase_mgr
                )
            if err:
                st.error(err)
            elif results is not None:
                cols, rows = results
                if coll_name:
                    st.caption(f"Collection: {coll_name}")
                df = pd.DataFrame(rows, columns=cols)
                st.subheader("Results")
                st.dataframe(df, use_container_width=True)
        elif send and not user_input.strip():
            st.warning("Enter a question first.")
    else:
        conn_str = _connection_string(st.session_state.db_choice, config)
        db = st.cache_resource(_get_db)(conn_str)
        show_schema = st.checkbox("Show schema", value=False)
        if show_schema:
            st.subheader("Schema")
            st.code(db.get_schema_text(), language="text")
        user_input = st.text_area(
            "Question", placeholder="e.g. How many employees? List all departments."
        )
        send = st.button("Run")
        if send and user_input.strip():
            with st.spinner("Querying..."):
                sql_or_decline, results, err = text_to_sql_run(user_input.strip(), db)
            if (
                DECLINE_MESSAGE in sql_or_decline
                or sql_or_decline.strip() == DECLINE_MESSAGE
            ):
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
