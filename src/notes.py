"""Заметки в консоли: добавить строку, показать все, удалить по номеру.

Заметки хранятся в data/notes.json в корне проекта — JSON-список строк.
Правила — чистые функции над списком; файл — load_notes/save_notes;
ввод с клавиатуры и печать — только в main().
"""

import json
import os
import sys
from pathlib import Path

# src/notes.py → корень проекта; верно при установке `pip install -e`.
NOTES_FILE = Path(__file__).resolve().parents[1] / "data" / "notes.json"


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


def add_note(notes: list[str], text: str) -> list[str]:
    """Вернуть новый список с заметкой в конце. Пустую строку не принимать."""
    text = text.strip()
    if not text:
        raise ValueError("Заметка не может быть пустой.")
    return [*notes, text]


def _check_number(notes: list[str], number: int) -> None:
    """Номер для человека начинается с 1."""
    if not 1 <= number <= len(notes):
        raise ValueError(f"Нет заметки с номером {number}.")


def delete_note(notes: list[str], number: int) -> list[str]:
    """Вернуть новый список без заметки с номером number."""
    _check_number(notes, number)
    return notes[: number - 1] + notes[number:]


def edit_note(notes: list[str], number: int, text: str) -> list[str]:
    """Вернуть новый список, где заметка с номером number заменена на text."""
    _check_number(notes, number)
    text = text.strip()
    if not text:
        raise ValueError("Заметка не может быть пустой.")
    return [*notes[: number - 1], text, *notes[number:]]


def format_notes(notes: list[str]) -> str:
    """Пронумерованный список для вывода на экран."""
    if not notes:
        return "Заметок нет."
    return "\n".join(f"{i}. {text}" for i, text in enumerate(notes, start=1))


MENU = """
1 — добавить заметку
2 — показать все
3 — удалить по номеру
4 — изменить по номеру
0 — выход"""


def parse_number(raw: str) -> int:
    """Номер из ввода человека; не число — ValueError."""
    raw = raw.strip()
    if not raw.isdigit():
        raise ValueError("Номер — целое положительное число.")
    return int(raw)


def main(path: Path = NOTES_FILE) -> None:
    try:
        notes = load_notes(path)
    except StorageError as error:
        # Файл не трогаем: перезапись пустым списком уничтожила бы заметки.
        sys.exit(f"{error}\nИсправьте или переименуйте файл и запустите снова.")
    while True:
        print(MENU)
        try:
            choice = input("> ").strip()
            if choice == "1":
                updated = add_note(notes, input("Текст: "))
                save_notes(path, updated)
                notes = updated
                print("Добавлено.")
            elif choice == "2":
                print(format_notes(notes))
            elif choice == "3":
                print(format_notes(notes))
                updated = delete_note(notes, parse_number(input("Номер: ")))
                save_notes(path, updated)
                notes = updated
                print("Удалено.")
            elif choice == "4":
                print(format_notes(notes))
                number = parse_number(input("Номер: "))
                _check_number(notes, number)  # до вопроса о тексте
                updated = edit_note(notes, number, input("Новый текст: "))
                save_notes(path, updated)
                notes = updated
                print("Изменено.")
            elif choice == "0":
                break
            else:
                print("Нет такого пункта.")
        except ValueError as error:
            print(error)
        except OSError as error:
            print(f"Не удалось сохранить, изменение отменено: {error}")
        except (EOFError, KeyboardInterrupt):
            print()
            break


if __name__ == "__main__":
    main()
