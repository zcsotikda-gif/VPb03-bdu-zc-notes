# zc-notes

Заметки в консоли: добавить строку, показать все, изменить и удалить по
номеру. Заметки сохраняются в `data/notes.json` и переживают перезапуск.

Учебный проект курса Zerocoder «Вайб-кодинг».

## Установка

Нужен Python 3.12 (Homebrew).

```
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

Ставить только с `-e`: путь к `data/` считается от `src/notes.py`.

## Запуск

```
.venv/bin/python -m notes
```

Программа показывает меню и ждёт номер пункта. Нумерация заметок — с 1. Если `data/notes.json` испорчен, программа
сообщит об ошибке и закроется, не трогая файл: исправьте или переименуйте его.

## Проверка

```
.venv/bin/pytest -v
.venv/bin/pytest tests/test_notes.py::test_edit_note_replaces_only_target
.venv/bin/ruff check src tests
```
