"""Хранение заметок в JSON-файле: JSON-список строк."""

import json
import os
from pathlib import Path

# src/notes/database.py → корень проекта; верно при установке `pip install -e`.
NOTES_FILE = Path(__file__).resolve().parents[2] / "data" / "notes.json"


class StorageError(Exception):
    """Файл заметок нельзя прочитать как JSON-список строк."""


def load_notes(path: Path) -> list[str]:
    """Прочитать заметки; нет файла — пустой список."""
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise StorageError(f"Не удалось прочитать {path}: {error}") from error
    if not isinstance(data, list) or not all(isinstance(n, str) for n in data):
        raise StorageError(f"В {path} ожидается JSON-список строк.")
    return data


def save_notes(path: Path, notes: list[str]) -> None:
    """Записать заметки целиком: сначала во временный файл, затем заменить.

    Замена атомарна, поэтому сбой посреди записи не портит прежний файл.
    """
    path.parent.mkdir(parents=True, exist_ok=True)  # data/ нет в git
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)
