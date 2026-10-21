"""Тесты меню: main() целиком на временном файле, ввод подменён."""

import json

import pytest

from notes import database
from notes.database import load_notes, save_notes
from notes.main import MENU, main


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
    main(path)
    out = capsys.readouterr().out
    assert "1. купить хлеб\n2. позвонить" in out
    assert "Изменено." in out
    assert "Удалено." in out
    assert out.rstrip().endswith("1. купить молоко\n" + MENU)
    assert json.loads(path.read_text(encoding="utf-8")) == ["купить молоко"]


def test_menu_reports_wrong_number(tmp_path, monkeypatch, capsys):
    path = tmp_path / "notes.json"
    save_notes(path, ["а"])
    feed(monkeypatch, "4", "x", "3", "5", "0")
    main(path)
    out = capsys.readouterr().out
    assert "Номер — целое положительное число." in out
    assert "Нет заметки с номером 5." in out
    assert load_notes(path) == ["а"]


def test_menu_edit_checks_number_before_text(tmp_path, monkeypatch, capsys):
    path = tmp_path / "notes.json"
    save_notes(path, ["а"])
    prompts = feed(monkeypatch, "4", "7", "0")
    main(path)
    assert "Нет заметки с номером 7." in capsys.readouterr().out
    assert "Новый текст: " not in prompts
    assert load_notes(path) == ["а"]


def test_notes_survive_restart(tmp_path, monkeypatch, capsys):
    path = tmp_path / "notes.json"
    feed(monkeypatch, "1", "запомнить", "0")
    main(path)
    feed(monkeypatch, "2", "0")
    main(path)
    assert "1. запомнить" in capsys.readouterr().out


def test_bad_file_stops_without_overwrite(tmp_path, monkeypatch):
    path = tmp_path / "notes.json"
    path.write_text("[oops", encoding="utf-8")
    feed(monkeypatch, "1", "новая", "0")
    with pytest.raises(SystemExit) as stop:
        main(path)
    assert "Не удалось прочитать" in str(stop.value.code)
    assert path.read_text(encoding="utf-8") == "[oops"


def test_failed_save_cancels_change(tmp_path, monkeypatch, capsys):
    path = tmp_path / "notes.json"

    def broken_save(path, notes):
        raise OSError("диск заполнен")

    monkeypatch.setattr(database, "save_notes", broken_save)
    feed(monkeypatch, "1", "потеряется", "2", "0")
    main(path)
    out = capsys.readouterr().out
    assert "Не удалось сохранить, изменение отменено: диск заполнен" in out
    assert "Заметок нет." in out
    assert not path.exists()
