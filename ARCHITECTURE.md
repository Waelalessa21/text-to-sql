# Project Architecture

## Overview

This document describes the high-level architecture of the `text-to-sql` project. It explains components, responsibilities, and how data flows through the system.

## Components

- Entrypoint: `main.py` — launches the application and wires components.
- API: `text_to_sql_engine/src/ai_engine/api/server.py` — serves the UI / handles requests.
- Core: `text_to_sql_engine/src/ai_engine/core/` — business logic for schema extraction and SQL generation (`get_db_schema.py`, `text_to_sql.py`).
- Model: `text_to_sql_engine/src/ai_engine/model/` — model loader and prompt construction (`loader.py`, `prompt.py`).
- Config: `text_to_sql_engine/src/ai_engine/config/` — settings and DB setup (`settings.py`, `setup_db.py`).
- UI: `text_to_sql_engine/src/ai_engine/ui/user_interface.py` — user-facing CLI or web UI glue.
- Data: `data/` — example datasets, SQL files, or fixtures.

## Data Flow (simplified)

1. `main.py` starts the service and initializes configuration.
2. Requests arrive at `api/server.py` (HTTP or CLI wrapper).
3. The API delegates to core services in `core/` to inspect DB schema (`get_db_schema.py`) and translate user text to a SQL plan (`text_to_sql.py`).
4. Core uses `model/loader.py` to load a model or client and `model/prompt.py` to build prompts.
5. Generated SQL is validated against schema; `config/setup_db.py` contains helpers to initialize example DBs.
6. Results are returned to the UI or API response.

## File Map (key files)

- `main.py`
- `requirements.txt`, `pyproject.toml`
- `text_to_sql_engine/src/ai_engine/api/server.py`
- `text_to_sql_engine/src/ai_engine/core/get_db_schema.py`
- `text_to_sql_engine/src/ai_engine/core/text_to_sql.py`
- `text_to_sql_engine/src/ai_engine/model/loader.py`
- `text_to_sql_engine/src/ai_engine/model/prompt.py`
- `text_to_sql_engine/src/ai_engine/config/settings.py`
- `text_to_sql_engine/src/ai_engine/config/setup_db.py`
- `text_to_sql_engine/src/ai_engine/ui/user_interface.py`

## Deployment / Run

- Install dependencies: `pip install -r requirements.txt` (or use `pyproject.toml`).
- Run locally: `python main.py` (the entrypoint will start the API/UI).

## Next steps / Suggestions

- Add a PlantUML or Mermaid diagram for visualization if you want richer docs.
- Extend this file with sequence diagrams for request handling or model prompts.
