# utils/config_reader.py
import json
from pathlib import Path


class ConfigReader:
    _cache = {}

    @staticmethod
    def load_config(file_name: str = "testsetting.json"):
        if file_name in ConfigReader._cache:
            return ConfigReader._cache[file_name]

        # FIXED: Lấy đường dẫn project root
        project_root = Path(__file__).resolve().parents[2]

        config_path = project_root / file_name

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        ConfigReader._cache[file_name] = data
        return data

