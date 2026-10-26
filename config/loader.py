"""Чтение настроек и тестовых данных без секретов."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_config(name: str) -> dict[str, Any]:
    """Прочитать JSON из каталога конфигурации."""
    with (ROOT / "config" / name).open(encoding="utf-8") as stream:
        return json.load(stream)
