"""Tests for the word morphology endpoints."""

from quranref import API_BASE


def url(path: str) -> str:
    return f"{API_BASE}/{path}"


class TestAyaWords:
    def test_tokens_in_reading_order(self, client):
        resp = client.get(url("aya-words/1:1"))
        assert resp.status_code == 200
        tokens = resp.json()
        assert [t["position"] for t in tokens] == [1, 2, 3, 4]
        first = tokens[0]
        assert first["text"] == "بِسْمِ"
        assert first["text_simple"] == "بسم"
        assert first["root"] == "سمو"
        assert first["lemma"] == "اسْم"
        assert first["glosses"] == {"english": "In (the) name"}
        assert first["segments"][0]["tag"] == "N"

    def test_unknown_aya_is_empty(self, client):
        resp = client.get(url("aya-words/9:9"))
        assert resp.status_code == 200
        assert resp.json() == []


class TestLemma:
    def test_lemma_with_meanings_and_occurrences(self, client):
        resp = client.get(url("lemma/رَحِيم"))
        assert resp.status_code == 200
        data = resp.json()
        assert data["root"] == "رحم"
        assert data["pos"] == "N"
        assert data["count"] == 2
        assert [o["aya_key"] for o in data["occurrences"]] == ["1:1", "1:3"]
        assert data["occurrences"][0]["text_simple"] == "الرحيم"
        assert data["occurrences"][0]["aya_text"] == ""  # fixture has no "simple" text type
        meanings = data["meanings"]["english"]
        assert {m["gloss"] for m in meanings} == {"the Most Merciful", "the Especially Merciful"}
        assert all(m["count"] == 1 for m in meanings)

    def test_lemma_occurrences_include_requested_text_type(self, client):
        resp = client.get(url("lemma/رَحِيم") + "?text_type=simple-clean")
        assert resp.status_code == 200
        first = resp.json()["occurrences"][0]
        assert first["aya_text"] == "بسم الله الرحمن الرحيم"

    def test_unknown_lemma(self, client):
        assert client.get(url("lemma/nope")).status_code == 404


class TestRoot:
    def test_root_lists_lemmas_with_counts(self, client):
        resp = client.get(url("root/رحم"))
        assert resp.status_code == 200
        data = resp.json()
        assert data["letters"] == 3
        assert data["count"] == 4
        assert {(x["lemma"], x["count"]) for x in data["lemmas"]} == {("رَحْمٰن", 2), ("رَحِيم", 2)}

    def test_unknown_root(self, client):
        assert client.get(url("root/xyz")).status_code == 404

    def test_roots_by_letter(self, client):
        resp = client.get(url("roots-by-letter/ر"))
        assert resp.status_code == 200
        assert resp.json() == [["رحم", 4]]


class TestWordMorphology:
    def test_word_form_maps_to_lemma_and_root(self, client):
        resp = client.get(url("word-morphology/الرحيم"))
        assert resp.status_code == 200
        assert resp.json() == [{"lemma": "رَحِيم", "root": "رحم", "pos": "N", "count": 2}]

    def test_word_without_morphology(self, client):
        resp = client.get(url("word-morphology/nothing"))
        assert resp.status_code == 200
        assert resp.json() == []
