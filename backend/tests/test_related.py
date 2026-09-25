"""Tests for similar ayas and recurring phrases."""

from quranref import API_BASE


def url(path: str) -> str:
    return f"{API_BASE}/{path}"


def test_related_lists_similar_ayas_with_texts_and_phrases(client):
    resp = client.get(url("related/1:1") + "?languages=arabic:simple-clean")
    assert resp.status_code == 200
    data = resp.json()
    assert [(s["aya_key"], s["score"], s["match_words"]) for s in data["similar"]] == [
        ("1:3", 80, [[3, 4]])
    ]
    assert data["similar"][0]["texts"]["arabic"]["simple-clean"] == "الرحمن الرحيم"
    assert [(p["id"], p["aya_count"], p["ranges"]) for p in data["phrases"]] == [
        ("phrase:1", 2, [[3, 4]])
    ]


def test_related_works_in_the_reverse_direction(client):
    data = client.get(url("related/1:3")).json()
    assert [s["aya_key"] for s in data["similar"]] == ["1:1"]
    assert data["phrases"][0]["ranges"] == [[1, 2]]


def test_related_for_isolated_aya(client):
    assert client.get(url("related/2:2")).json() == {"similar": [], "phrases": []}


def test_phrase_and_its_ayas(client):
    phrase = client.get(url("phrase/phrase:1")).json()
    assert phrase["text"] == "ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"
    assert phrase["aya_keys"] == ["1:1", "1:3"]
    page = client.get(url("phrase/phrase:1/ayas") + "?languages=arabic:simple-clean").json()
    assert page["total"] == 2
    assert [a["aya_key"] for a in page["ayas"]] == ["1:1", "1:3"]
    assert client.get(url("phrase/nope")).status_code == 404
