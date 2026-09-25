"""Tests for the tafsir importer and endpoints."""

import json

import pytest
from quranref import API_BASE
from quranref.tafsir import import_tafsir, parse_qul_tafsir
from sqlalchemy.orm import sessionmaker


def url(path: str) -> str:
    return f"{API_BASE}/{path}"


QUL_SAMPLE = {
    "1:1": {"text": "<p>On the basmala.</p>", "ayah_keys": ["1:1"]},
    "1:2": {"text": "Praise, covering two ayas.", "ayah_keys": ["1:2", "1:3"]},
    "1:3": "1:2",
    "2:1": {"text": "", "ayah_keys": ["2:1"]},
    "2:2": {"text": "The Book."},
}


def test_parse_qul_tafsir_groups_ayas_and_skips_empty_passages():
    passages = parse_qul_tafsir(QUL_SAMPLE)
    assert passages == [
        (["1:1"], "<p>On the basmala.</p>"),
        (["1:2", "1:3"], "Praise, covering two ayas."),
        (["2:2"], "The Book."),
    ]


@pytest.fixture
def tafsir_file(tmp_path):
    path = tmp_path / "tafsir.json"
    path.write_text(json.dumps(QUL_SAMPLE), encoding="utf-8")
    return path


def test_import_and_lookup(client, test_engine, tafsir_file):
    session_factory = sessionmaker(bind=test_engine)
    with session_factory() as session:
        counts = import_tafsir(
            session, tafsir_file, "test-en", "Test Tafsir", "english", author="Someone"
        )
    assert counts == (3, 4)

    listing = client.get(url("tafsirs")).json()
    assert [t["slug"] for t in listing] == ["test-en"]
    assert listing[0]["author"] == "Someone"

    grouped = client.get(url("tafsir/test-en/1:3")).json()
    assert grouped["from_key"] == "1:2" and grouped["to_key"] == "1:3"
    assert grouped["aya_keys"] == ["1:2", "1:3"]
    assert grouped["text"] == "Praise, covering two ayas."
    assert grouped["name"] == "Test Tafsir"
    assert client.get(url("tafsir/test-en/2:1")).status_code == 404
    assert client.get(url("tafsir/other/1:1")).status_code == 404

    # Re-import with the same slug replaces the passages instead of duplicating them
    with session_factory() as session:
        counts = import_tafsir(session, tafsir_file, "test-en", "Renamed", "english")
    assert counts == (3, 4)
    assert client.get(url("tafsir/test-en/1:1")).json()["name"] == "Renamed"
    with session_factory() as session:
        from quranref.sql_models import TafsirEntry, TafsirText

        assert session.query(TafsirText).count() == 3
        assert session.query(TafsirEntry).count() == 4
