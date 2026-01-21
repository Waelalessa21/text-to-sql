# Text-to-SQL Project Architecture

## Overview
Text-to-SQL is a project that converts natural language text into SQL queries using AI models. The architecture is organized into modular components that handle different aspects of the system.

## Project Structure

```
text-to-sql/
├── main.py                          # Entry point of the application
├── pyproject.toml                   # Project metadata and dependencies
├── requirements.txt                 # Python package dependencies
├── README.md                        # Project documentation
└── text_to_sql_engine/
    └── src/
        └── ai_engine/
            ├── api/
            │   └── server.py        # REST API server and endpoints
            ├── config/
            │   └── settings.py      # Configuration and environment settings
            ├── core/
            │   └── text_to_sql.py   # Main text-to-SQL conversion logic
            ├── model/
            │   ├── loader.py        # Model loading utilities
            │   └── prompt.py        # Prompt templates and engineering
            └── ui/
                └── user_interface.py # User interface component
```

## Component Architecture

### 1. **API Layer** (`api/server.py`)
- Exposes REST API endpoints for text-to-SQL conversion
- Handles HTTP requests and responses
- Integrates with the core conversion engine

### 2. **Configuration Layer** (`config/settings.py`)
- Manages application settings and environment variables
- Stores configuration parameters for model, API, and database connections
- Centralizes configuration management across the application

### 3. **Core Engine** (`core/text_to_sql.py`)
- Main business logic for converting text to SQL queries
- Orchestrates the text processing and SQL generation pipeline
- Coordinates between model, prompt, and other components

### 4. **Model Layer** (`model/`)
- **loader.py**: Loads and initializes AI models
- **prompt.py**: Manages prompt templates and prompt engineering strategies
- Handles model inference and text embeddings

### 5. **User Interface** (`ui/user_interface.py`)
- Provides user-facing interface for the application
- Could be CLI, web UI, or other interface types
- Communicates with the core engine or API

### 6. **Entry Point** (`main.py`)
- Application startup point
- Initializes the system and manages application lifecycle

## Data Flow

```
User Input (UI/API)
        ↓
    API Server / User Interface
        ↓
    Core Engine (text_to_sql.py)
        ↓
    Model + Prompt Generation
        ↓
    SQL Query Output
```

## Key Dependencies
- Python >= 3.11
- Additional dependencies defined in `requirements.txt` and `pyproject.toml`

## Module Responsibilities

| Module | Responsibility |
|--------|---|
| `server.py` | Handle HTTP requests, route to engine, return responses |
| `settings.py` | Load and manage configuration from environment |
| `text_to_sql.py` | Orchestrate text-to-SQL pipeline |
| `loader.py` | Initialize and cache AI models |
| `prompt.py` | Create optimized prompts for the model |
| `user_interface.py` | Present UI to end users |
| `main.py` | Bootstrap application |

## Design Patterns

- **Modular Architecture**: Each component has a single responsibility
- **Separation of Concerns**: API, configuration, and business logic are isolated
- **Layered Architecture**: Clear separation between presentation, business logic, and configuration layers
- **Dependency Injection**: Components can be easily configured and tested
