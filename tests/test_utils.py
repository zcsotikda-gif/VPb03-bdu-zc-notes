"""Тесты правил: добавление, удаление, исправление и вывод заметок."""

import pytest

from notes.utils import add_note, delete_note, edit_note, format_notes


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
