"""Tests for the word gloss importer (uses the seeded test graph)."""

import json
from pathlib import Path

import pytest
from quranref.glosses import _import_with_cypher, import_word_glosses, load_gloss_file
from quranref.models import Token


def test_load_gloss_file_accepts_map_and_list(tmp_path: Path):
    as_map = tmp_path / "map.json"
    as_map.write_text(json.dumps({"1:1:1": "In (the) name", "1:1:2": ""}), encoding="utf-8")
    assert load_gloss_file(as_map) == {"1:1:1": "In (the) name"}

    as_list = tmp_path / "list.json"
    as_list.write_text(
        json.dumps(
            [
                {"surah": 1, "ayah": 1, "word": 3, "text": "the Most Gracious"},
                {"location": "1:1:4", "translation": "the Most Merciful"},
            ]
        ),
        encoding="utf-8",
    )
    assert load_gloss_file(as_list) == {"1:1:3": "the Most Gracious", "1:1:4": "the Most Merciful"}


@pytest.fixture
def scratch_tokens(test_graph):
    """Two throwaway tokens, removed again after the test so the seed data stays intact."""
    test_graph.bulk_add(
        [
            Token(
                id="99:1:1",
                surah_number=99,
                aya_number=1,
                position=1,
                text="أ",
                tag="N",
                glosses={"english": "first"},
            ),
            Token(id="99:1:2", surah_number=99, aya_number=1, position=2, text="ب", tag="N"),
        ]
    )
    yield
    test_graph.cypher("MATCH (t:Token) WHERE t.surah_number = 99 DETACH DELETE t")


def _glosses(g, token_id: str) -> dict:
    rows = g.cypher(
        "MATCH (t:Token {id: $id}) RETURN t.id, t.glosses", columns=["id", "glosses"], id=token_id
    )
    return rows[0]["glosses"] or {}


def test_import_glosses_merges_languages_and_skips_unknown_tokens(
    test_graph, test_db, scratch_tokens
):
    updated = import_word_glosses(
        test_graph, test_db, "urdu", {"99:1:1": " پہلا ", "99:1:2": "دوسرا", "99:9:9": "ignored"}
    )
    assert updated == 2
    assert _glosses(test_graph, "99:1:1") == {"english": "first", "urdu": "پہلا"}
    assert _glosses(test_graph, "99:1:2") == {"urdu": "دوسرا"}

    # Re-importing a language replaces only that language
    import_word_glosses(test_graph, test_db, "urdu", {"99:1:1": "اول"})
    assert _glosses(test_graph, "99:1:1") == {"english": "first", "urdu": "اول"}


def test_cypher_fallback_behaves_the_same(test_graph, scratch_tokens):
    updated = _import_with_cypher(test_graph, "urdu", {"99:1:1": "پہلا", "99:9:9": "ignored"})
    assert updated == 1
    assert _glosses(test_graph, "99:1:1") == {"english": "first", "urdu": "پہلا"}
