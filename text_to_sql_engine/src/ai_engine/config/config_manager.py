import json
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: str = "user_config.json"):
        self.config_path = Path(config_path)
        self.config_data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file {self.config_path} not found.")
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config_data, f, indent=4, ensure_ascii=False)

    def get_active_db_info(self) -> Dict[str, Any]:
        active_key = self.config_data.get("active_db_key")
        for db in self.config_data.get("databases", []):
            if db["id"] == active_key:
                return db
        return self.config_data["databases"][0]
    
    def get_user_name(self) -> str:
        return self.config_data["user_info"]["name"]
    # --- الدوال الجديدة ---

    def add_database(self, db_id: str, name: str, db_type: str, url: str):
        new_db = {
            "id": db_id,
            "name": name,
            "type": db_type,
            "url": url
        }
        self.config_data["databases"].append(new_db)
        self._save_config()
        print(f"✅ Database '{name}' added successfully.")

    def switch_active_db(self, db_id: str):
        self.config_data["active_db_key"] = db_id
        self._save_config()
        
    def add_custom_schema(self, name: str, schema_text: str):
        if "custom_schemas" not in self.config_data:
            self.config_data["custom_schemas"] = []
            
        new_schema = {
            "id": name.lower().replace(" ", "_"),
            "name": name,
            "schema_text": schema_text
        }
        self.config_data["custom_schemas"].append(new_schema)
        self._save_config()
    
    def get_all_sources(self):
        sources = []
        for db in self.config_data.get("databases", []):
            sources.append({"id": db["id"], "name": db["name"], "type": "real_db"})
        for schema in self.config_data.get("custom_schemas", []):
            sources.append({"id": schema["id"], "name": schema["name"], "type": "schema_only"})
        return sources

    def get_source_by_id(self, source_id: str):

        for db in self.config_data.get("databases", []):
            if db["id"] == source_id:
                return db, "real_db"

        for schema in self.config_data.get("custom_schemas", []):
            if schema["id"] == source_id:
                return schema, "schema_only"
        return None, None