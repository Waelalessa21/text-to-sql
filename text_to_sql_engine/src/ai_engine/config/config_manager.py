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

    def get_active_db_info(self) -> Dict[str, Any]:
        active_key = self.config_data.get("active_db_key")
        for db in self.config_data.get("databases", []):
            if db["id"] == active_key:
                return db
        return self.config_data["databases"][0]