"""Тесты хранения в JSON. Только временные файлы из tmp_path."""

import pytest

from notes.database import StorageError, load_notes, save_notes


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
