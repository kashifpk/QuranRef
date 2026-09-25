"""Tests for the mushaf structure endpoints."""

from quranref import API_BASE


def url(path: str) -> str:
    return f"{API_BASE}/{path}"


def test_structure_tables(client):
    data = client.get(url("structure")).json()
    assert data["juz"][0]["verse_mapping"] == {"1": "1-3", "2": "1-2"}
    assert data["ruku"][0]["surah_ruku_number"] == 1
    assert data["hizb"] == []


def test_aya_structure(client):
    resp = client.get(url("structure/aya/2:2"))
    assert resp.status_code == 200
    assert resp.json() == {
        "aya_key": "2:2",
        "juz": 1,
        "hizb": 1,
        "rub": 1,
        "manzil": 1,
        "ruku": 2,
        "surah_ruku": 1,
        "sajda": "optional",
    }
    assert client.get(url("structure/aya/9:9")).status_code == 404


def test_surah_markers(client):
    markers = client.get(url("structure/surah/2")).json()
    assert markers == [
        {
            "aya_number": 1,
            "juz_start": 1,
            "hizb_start": 1,
            "rub_start": 1,
            "manzil_start": 1,
            "ruku_start": 1,
            "sajda": None,
        },
        {
            "aya_number": 2,
            "juz_start": None,
            "hizb_start": None,
            "rub_start": None,
            "manzil_start": None,
            "ruku_start": None,
            "sajda": "optional",
        },
    ]


def test_surah_info_languages(client):
    resp = client.get(url("surah-info/1"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["language"] == "english"
    assert data["available"] == ["english", "urdu"]
    assert "The Opening" in data["text"]
    urdu = client.get(url("surah-info/1") + "?language=urdu").json()
    assert urdu["language"] == "urdu" and "الفاتحہ" in urdu["text"]
    missing = client.get(url("surah-info/1") + "?language=french").json()
    assert missing["language"] == "english"  # falls back to what exists
    assert client.get(url("surah-info/2")).status_code == 404
