"""Правила работы с заметками: чистые функции над списком строк.

Не трогают ни файл, ни консоль: принимают список и возвращают новый.
Ошибка ввода — ValueError с текстом для человека.
"""


def add_note(notes: list[str], text: str) -> list[str]:
    """Вернуть новый список с заметкой в конце. Пустую строку не принимать."""
    text = text.strip()
    if not text:
        raise ValueError("Заметка не может быть пустой.")
    return [*notes, text]


def check_number(notes: list[str], number: int) -> None:
    """Номер для человека начинается с 1."""
    if not 1 <= number <= len(notes):
        raise ValueError(f"Нет заметки с номером {number}.")


def delete_note(notes: list[str], number: int) -> list[str]:
    """Вернуть новый список без заметки с номером number."""
    check_number(notes, number)
    return notes[: number - 1] + notes[number:]


def edit_note(notes: list[str], number: int, text: str) -> list[str]:
    """Вернуть новый список, где заметка с номером number заменена на text."""
    check_number(notes, number)
    text = text.strip()
    if not text:
        raise ValueError("Заметка не может быть пустой.")
    return [*notes[: number - 1], text, *notes[number:]]


def format_notes(notes: list[str]) -> str:
    """Пронумерованный список для вывода на экран."""
    if not notes:
        return "Заметок нет."
    return "\n".join(f"{i}. {text}" for i, text in enumerate(notes, start=1))
