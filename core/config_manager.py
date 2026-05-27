import json
import os
import sys
import traceback
from pathlib import Path


def _get_app_dir() -> Path:
    """Get the directory where config and data files should be stored."""
    if getattr(sys, "frozen", False):
        # Try multiple methods to find the real .exe directory
        candidates = []

        # Method 1: Windows API - most reliable
        try:
            import ctypes
            buf = ctypes.create_unicode_buffer(512)
            ctypes.windll.kernel32.GetModuleFileNameW(None, buf, 512)
            exe_path = Path(buf.value)
            candidates.append(exe_path.parent)
        except Exception:
            pass

        # Method 2: sys.argv[0]
        try:
            candidates.append(Path(sys.argv[0]).resolve().parent)
        except Exception:
            pass

        # Method 3: current working directory
        candidates.append(Path(os.getcwd()))

        # Pick the first directory that either has config.json or is writable
        for d in candidates:
            if (d / "config.json").exists():
                return d
        for d in candidates:
            try:
                test = d / "._billaccount_probe"
                test.write_text("ok")
                test.unlink()
                return d
            except OSError:
                continue

        return candidates[0] if candidates else Path(os.getcwd())
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
                self._debug_log(f"LOADED from {self.config_path}: bg={self.data.get('background_path', '(none)')}")
            except (json.JSONDecodeError, IOError):
                self.data = {}
                self._debug_log(f"FAILED to load {self.config_path}")
        for key, value in DEFAULT_CONFIG.items():
            if key not in self.data:
                self.data[key] = value

    def save(self):
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            if not self.config_path.exists():
                raise IOError("Config file not found after write")
            self._debug_log(f"OK: saved to {self.config_path}")
        except Exception as e:
            self._debug_log(f"FAIL: {self.config_path} -> {e}")
            fallback = Path.home() / ".billaccount" / "config.json"
            try:
                fallback.parent.mkdir(parents=True, exist_ok=True)
                with open(fallback, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=2)
                self.config_path = fallback
                self._app_dir = fallback.parent
                self._debug_log(f"FALLBACK: saved to {fallback}")
            except Exception as e2:
                self._debug_log(f"FALLBACK FAIL: {e2}")

    def _debug_log(self, msg):
        try:
            log_path = self.config_path.parent / "config_debug.log"
            with open(log_path, "a", encoding="utf-8") as f:
                import datetime
                ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{ts}] {msg}\n")
                f.write(f"  frozen={getattr(sys, 'frozen', False)}\n")
                f.write(f"  sys.executable={sys.executable}\n")
                f.write(f"  sys.argv[0]={sys.argv[0]}\n")
                f.write(f"  config_path={self.config_path}\n")
                f.write(f"  app_dir={self._app_dir}\n\n")
        except Exception:
            pass

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
