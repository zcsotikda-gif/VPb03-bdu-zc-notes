"""Точка входа: консольное меню заметок.

Единственное место, где соединяются части: правила (utils), хранение
(database) и консоль — input/print живут только здесь.
"""

import sys
from pathlib import Path

from notes import database, utils

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


def main(path: Path = database.NOTES_FILE) -> None:
    try:
        notes = database.load_notes(path)
    except database.StorageError as error:
        # Файл не трогаем: перезапись пустым списком уничтожила бы заметки.
        sys.exit(f"{error}\nИсправьте или переименуйте файл и запустите снова.")
    while True:
        print(MENU)
        try:
            choice = input("> ").strip()
            if choice == "1":
                updated = utils.add_note(notes, input("Текст: "))
                database.save_notes(path, updated)
                notes = updated
                print("Добавлено.")
            elif choice == "2":
                print(utils.format_notes(notes))
            elif choice == "3":
                print(utils.format_notes(notes))
                updated = utils.delete_note(notes, parse_number(input("Номер: ")))
                database.save_notes(path, updated)
                notes = updated
                print("Удалено.")
            elif choice == "4":
                print(utils.format_notes(notes))
                number = parse_number(input("Номер: "))
                utils.check_number(notes, number)  # до вопроса о тексте
                updated = utils.edit_note(notes, number, input("Новый текст: "))
                database.save_notes(path, updated)
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
