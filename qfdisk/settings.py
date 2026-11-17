"""Portable settings: stored in a `data` folder next to the exe (falls back to %AppData% if that is read-only)."""
from __future__ import annotations

import json
import os
import sys

DEFAULTS = {"language": "ar", "theme": "dark", "roots": [], "min_mb": 1}


def base_dir() -> str:
    d = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return d


def data_dir() -> str:
    d = os.path.join(base_dir(), "data")
    try:
        os.makedirs(d, exist_ok=True)
        t = os.path.join(d, ".w")
        with open(t, "w") as f:
            f.write("1")
        os.remove(t)
        return d
    except OSError:
        d = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "QFDiskCleaner")
        os.makedirs(d, exist_ok=True)
        return d


class Settings(dict):
    def __init__(self):
        super().__init__(DEFAULTS)
        self.path = os.path.join(data_dir(), "settings.json")
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.update(json.load(f))
        except (OSError, ValueError):
            pass

    def save(self) -> None:
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(dict(self), f, ensure_ascii=False, indent=2)
        except OSError:
            pass
