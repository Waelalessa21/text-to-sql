# text-to-sql


## Project Status

Core components have been implemented, and the system is currently focused on evaluating and comparing different pre-trained text-to-SQL models. currently we are satisfied with qwen2.5-coder:7b


## Completed Work

- Test Database preparation has been completed

- Data-to-schema conversion process has been implemented

- Schema passing mechanism to the model has been defined and tested

- Initial text-to-SQL pipeline structure has been set up

- Local LLM integration via Ollama completed  


## Current Phase

- Refining prompt design and schema formatting 

- Setup a way to work on external DB connections.

- Working on SQL validator


## Running the Project (Step-by-Step)


### 1. Install Ollama using this command or through the link: https://ollama.com/download

```bash
curl -fsSL https://ollama.com/install.sh | sh
```


### 2. Open Ollama

### 3. Pull the Model "qwen2.5"

```bash
ollama pull qwen2.5-coder:7b
```

### 4. Create and Activate a Virtual Environment
```bash
uv venv
source .venv/bin/activate
```

### 5. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 6. run test ui "we will move this to our website sooooon!!"

```bash
streamlit run src/ai_engine/ui/user_interface.py
```
