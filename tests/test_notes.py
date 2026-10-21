"""Тесты notes.py: правила, хранение в JSON и сценарии меню.

Боевой notes.json не трогается — везде временный файл из tmp_path.
"""

import json

import pytest

import notes
from notes import (
    StorageError,
    add_note,
    delete_note,
    edit_note,
    format_notes,
    load_notes,
    save_notes,
)

# --- правила ---------------------------------------------------------------


def test_add_note_appends_to_end():
    assert add_note(["первая"], "вторая") == ["первая", "вторая"]


def test_add_note_strips_spaces():
    assert add_note([], "  купить хлеб  ") == ["купить хлеб"]


@pytest.mark.parametrize("text", ["", "   ", "\t\n"])
def test_add_note_rejects_empty(text):
    with pytest.raises(ValueError, match="пустой"):
        add_note([], text)


def test_add_note_keeps_original_list():
    original = ["первая"]
    add_note(original, "вторая")
    assert original == ["первая"]


def test_delete_note_by_number_from_one():
    assert delete_note(["а", "б", "в"], 2) == ["а", "в"]


@pytest.mark.parametrize("number", [0, -1, 4])
def test_delete_note_rejects_wrong_number(number):
    with pytest.raises(ValueError, match=f"номером {number}"):
        delete_note(["а", "б", "в"], number)


def test_delete_note_keeps_original_list():
    original = ["а", "б"]
    delete_note(original, 1)
    assert original == ["а", "б"]


def test_edit_note_replaces_only_target():
    assert edit_note(["а", "б", "в"], 2, "  новое  ") == ["а", "новое", "в"]


@pytest.mark.parametrize("number", [0, 4])
def test_edit_note_rejects_wrong_number(number):
    with pytest.raises(ValueError, match=f"номером {number}"):
        edit_note(["а", "б", "в"], number, "новое")


def test_edit_note_rejects_empty_text():
    with pytest.raises(ValueError, match="пустой"):
        edit_note(["а"], 1, "   ")


def test_edit_note_keeps_original_list():
    original = ["а", "б"]
    edit_note(original, 1, "новое")
    assert original == ["а", "б"]


def test_format_notes_numbers_from_one():
    assert format_notes(["а", "б"]) == "1. а\n2. б"


def test_format_notes_empty():
    assert format_notes([]) == "Заметок нет."


# --- хранение --------------------------------------------------------------


def test_load_missing_file_is_empty(tmp_path):
    assert load_notes(tmp_path / "notes.json") == []


def test_save_then_load_keeps_cyrillic(tmp_path):
    path = tmp_path / "notes.json"
    save_notes(path, ["купить хлеб", "позвонить"])
    assert load_notes(path) == ["купить хлеб", "позвонить"]
    assert "купить хлеб" in path.read_text(encoding="utf-8")


def test_save_creates_missing_dir(tmp_path):
    path = tmp_path / "data" / "notes.json"
    save_notes(path, ["а"])
    assert load_notes(path) == ["а"]


def test_save_leaves_no_tmp_file(tmp_path):
    save_notes(tmp_path / "notes.json", ["а"])
    assert [p.name for p in tmp_path.iterdir()] == ["notes.json"]


@pytest.mark.parametrize("content", ["[oops", '{"a": 1}', "[1, 2]"])
def test_load_rejects_bad_file(tmp_path, content):
    path = tmp_path / "notes.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(StorageError):
        load_notes(path)


# --- меню ------------------------------------------------------------------


def feed(monkeypatch, *answers):
    """Подставить ответы на input(); когда кончатся — EOF, main() выходит.

    Возвращает список заданных вопросов (приглашений input).
    """
    queue = iter(answers)
    prompts = []

    def fake_input(prompt=""):
        prompts.append(prompt)
        try:
            return next(queue)
        except StopIteration:
            raise EOFError from None

    monkeypatch.setattr("builtins.input", fake_input)
    return prompts


def test_menu_add_show_edit_delete(tmp_path, monkeypatch, capsys):
    path = tmp_path / "notes.json"
    feed(
        monkeypatch,
        "1", "купить хлеб",
        "1", "позвонить",
        "2",
        "4", "1", "купить молоко",
        "3", "2",
        "2",
        "0",
    )
    notes.main(path)
    out = capsys.readouterr().out
    assert "1. купить хлеб\n2. позвонить" in out
    assert "Изменено." in out
    assert "Удалено." in out
    assert out.rstrip().endswith("1. купить молоко\n" + notes.MENU)
    assert json.loads(path.read_text(encoding="utf-8")) == ["купить молоко"]


def test_menu_reports_wrong_number(tmp_path, monkeypatch, capsys):
    path = tmp_path / "notes.json"
    save_notes(path, ["а"])
    feed(monkeypatch, "4", "x", "3", "5", "0")
    notes.main(path)
    out = capsys.readouterr().out
    assert "Номер — целое положительное число." in out
    assert "Нет заметки с номером 5." in out
    assert load_notes(path) == ["а"]


def test_menu_edit_checks_number_before_text(tmp_path, monkeypatch, capsys):
    path = tmp_path / "notes.json"
    save_notes(path, ["а"])
    prompts = feed(monkeypatch, "4", "7", "0")
    notes.main(path)
    assert "Нет заметки с номером 7." in capsys.readouterr().out
    assert "Новый текст: " not in prompts
    assert load_notes(path) == ["а"]


def test_notes_survive_restart(tmp_path, monkeypatch, capsys):
    path = tmp_path / "notes.json"
    feed(monkeypatch, "1", "запомнить", "0")
    notes.main(path)
    feed(monkeypatch, "2", "0")
    notes.main(path)
    assert "1. запомнить" in capsys.readouterr().out


def test_bad_file_stops_without_overwrite(tmp_path, monkeypatch):
    path = tmp_path / "notes.json"
    path.write_text("[oops", encoding="utf-8")
    feed(monkeypatch, "1", "новая", "0")
    with pytest.raises(SystemExit) as stop:
        notes.main(path)
    assert "Не удалось прочитать" in str(stop.value.code)
    assert path.read_text(encoding="utf-8") == "[oops"


def test_failed_save_cancels_change(tmp_path, monkeypatch, capsys):
    path = tmp_path / "notes.json"

    def broken_save(path, notes):
        raise OSError("диск заполнен")

    monkeypatch.setattr(notes, "save_notes", broken_save)
    feed(monkeypatch, "1", "потеряется", "2", "0")
    notes.main(path)
    out = capsys.readouterr().out
    assert "Не удалось сохранить, изменение отменено: диск заполнен" in out
    assert "Заметок нет." in out
    assert not path.exists()
