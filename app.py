import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# إضافة المسار لضمان استيراد المكتبات الخاصة بك
BASE_DIR = Path(__file__).resolve().parent
SRC_PATH = BASE_DIR / "text_to_sql_engine" / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from ai_engine.config.config_manager import ConfigManager
from ai_engine.core.database_manager import DatabaseManager
from ai_engine.core.text_to_sql import TextToSQLEngine

# --- إعدادات الصفحة ---
st.set_page_config(page_title="SQL Assistant Pro", page_icon="🪄", layout="wide")

# تهيئة الإعدادات في Session State لضمان عدم إعادة التحميل غير الضرورية
if 'config' not in st.session_state:
    st.session_state.config = ConfigManager()
if 'engine' not in st.session_state:
    st.session_state.engine = None
if 'current_source_type' not in st.session_state:
    st.session_state.current_source_type = None

# --- القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.title("🚀 Control Panel")
    
    # القائمة الرئيسية التي طلبتها (الخيارات الأربعة)
    menu_choice = st.radio(
        "Main Menu:",
        ["1. Question Loop", "2. DB Info & Schema", "3. Select Source (DB/Schema)", "4. Add New Source"]
    )
    
    st.divider()
    
    # عرض الحالة الحالية
    if st.session_state.engine:
        st.success(f"Mode: {st.session_state.current_source_type.upper()} Active")
    else:
        st.warning("No Source Connected")

# --- التنفيذ بناءً على خيار القائمة ---

# الخيار 3: اختيار المصدر (البداية المنطقية)
if menu_choice == "3. Select Source (DB/Schema)":
    st.header("🔌 Connection Manager")
    
    # جلب المصادر من الكونسول
    all_sources = st.session_state.config.get_all_sources()
    source_names = [s['name'] for s in all_sources]
    
    selected_name = st.selectbox("Choose a Database or Mock Schema:", source_names)
    
    if st.button("Connect & Initialize AI"):
        source_data, s_type = st.session_state.config.get_source_by_id(
            next(s['id'] for s in all_sources if s['name'] == selected_name)
        )
        
        with st.spinner("Loading environment..."):
            if s_type == "real_db":
                db_manager = DatabaseManager(source_data['url'])
                st.session_state.engine = TextToSQLEngine(db_manager)
                st.session_state.active_schema = None # يسحبها تلقائياً من DB
            else:
                # وضع السكيما فقط
                st.session_state.engine = TextToSQLEngine(None)
                st.session_state.active_schema = source_data['schema_text']
            
            st.session_state.current_source_type = s_type
            st.session_state.active_source_name = selected_name
            st.success(f"Successfully connected to {selected_name}!")

# الخيار 1: حلقة الأسئلة
elif menu_choice == "1. Question Loop":
    st.header(f"💬 Chatting with: {st.session_state.get('active_source_name', 'None')}")
    
    if not st.session_state.engine:
        st.info("👈 Please go to 'Select Source' first to initialize the engine.")
    else:
        user_query = st.chat_input("Type your question here (e.g., 'Show me top 5 products')...")
        
        if user_query:
            with st.chat_message("user"):
                st.write(user_query)
            
            with st.chat_message("assistant"):
                try:
                    # معالجة الاستعلام بناءً على النوع
                    if st.session_state.current_source_type == "real_db":
                        sql, cols, rows = st.session_state.engine.process_query(user_query)
                        st.code(sql, language="sql")
                        if rows:
                            st.dataframe(pd.DataFrame(rows, columns=cols), use_container_width=True)
                        else:
                            st.write("No data returned.")
                    else:
                        # وضع السكيما النصية
                        sql, _, _ = st.session_state.engine.process_query(
                            user_query, 
                            custom_schema=st.session_state.active_schema
                        )
                        st.info("🛠️ Schema-Only Mode: SQL Generated but not executed.")
                        st.code(sql, language="sql")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

# الخيار 2: المعلومات والسكيما
elif menu_choice == "2. DB Info & Schema":
    st.header("📊 Source Metadata")
    if not st.session_state.engine:
        st.warning("Connect to a source to see details.")
    else:
        if st.session_state.current_source_type == "real_db":
            st.subheader("Database Schema (Reflected)")
            st.code(st.session_state.engine.db_manager.get_schema_text(), language="text")
        else:
            st.subheader("Mock Schema (Custom Text)")
            st.text_area("Schema Definition", st.session_state.active_schema, height=300)

# الخيار 4: إضافة مصدر جديد
elif menu_choice == "4. Add New Source":
    st.header("🆕 Add New Entry")
    tab1, tab2 = st.tabs(["Real Database", "Mock Schema"])
    
    with tab1:
        with st.form("add_db"):
            db_id = st.text_input("Unique ID (e.g. prod_db)")
            db_name = st.text_input("Display Name")
            db_url = st.text_input("SQLAlchemy URL (e.g. sqlite:///test.db)")
            if st.form_submit_button("Save Database"):
                st.session_state.config.add_database(db_id, db_name, "db", db_url)
                st.success("Database added to config!")

    with tab2:
        with st.form("add_schema"):
            sc_name = st.text_input("Schema Name (e.g. Hospital Mock)")
            sc_text = st.text_area("Schema Content (Table: x, columns: y...)")
            if st.form_submit_button("Save Mock Schema"):
                st.session_state.config.add_custom_schema(sc_name, sc_text)
                st.success("Mock Schema saved to config!")