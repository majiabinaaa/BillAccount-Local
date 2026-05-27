import json
import os
import sys
from pathlib import Path


def _get_app_dir() -> Path:
    """Get the directory where config and data files should be stored."""
    if getattr(sys, "frozen", False):
        try:
            import ctypes
            buf = ctypes.create_unicode_buffer(512)
            ctypes.windll.kernel32.GetModuleFileNameW(None, buf, 512)
            return Path(buf.value).parent
        except Exception:
            return Path(os.path.dirname(os.path.abspath(sys.argv[0])))
    else:
        return Path(__file__).parent.parent


DEFAULT_CONFIG = {
    "theme": "dark",
    "data_path": "",
    "window_width": 1050,
    "window_height": 700,
}


class ConfigManager:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = _get_app_dir() / "config.json"
        self.config_path = Path(config_path)
        self._app_dir = self.config_path.parent
        self.data = {}
        self.load()

    def load(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.data = {}
        for key, value in DEFAULT_CONFIG.items():
            if key not in self.data:
                self.data[key] = value

    def save(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value):
        self.data[key] = value
        self.save()

    @property
    def theme(self) -> str:
        return self.get("theme", "dark")

    @theme.setter
    def theme(self, value: str):
        self.set("theme", value)

    @property
    def data_path(self) -> str:
        path = self.get("data_path", "")
        if not path:
            path = str(self._app_dir / "bill_data.db")
        p = Path(path)
        if p.is_dir() or p.suffix != ".db":
            p = p / "bill_data.db"
        return str(p)

    @data_path.setter
    def data_path(self, value: str):
        p = Path(value)
        if p.is_dir() or p.suffix != ".db":
            p = p / "bill_data.db"
        self.set("data_path", str(p.resolve()))
