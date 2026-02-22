"""Integration tests for QuranRef API endpoints."""

from quranref import API_BASE


def url(path: str) -> str:
    return f"{API_BASE}/{path}"


class TestGetLetters:
    def test_returns_arabic_letters(self, client):
        resp = client.get(url("letters"))
        assert resp.status_code == 200
        letters = resp.json()
        assert len(letters) == 31

    def test_contains_known_letters(self, client):
        resp = client.get(url("letters"))
        letters = resp.json()
        assert "ا" in letters
        assert "ب" in letters
        assert "ي" in letters


class TestGetSurahs:
    def test_returns_seeded_surahs(self, client):
        resp = client.get(url("surahs"))
        assert resp.status_code == 200
        surahs = resp.json()
        assert len(surahs) == 2

    def test_sorted_by_number(self, client):
        resp = client.get(url("surahs"))
        surahs = resp.json()
        assert surahs[0]["surah_number"] == 1
        assert surahs[1]["surah_number"] == 2

    def test_has_expected_fields(self, client):
        resp = client.get(url("surahs"))
        surah = resp.json()[0]
        expected_fields = [
            "id", "surah_number", "arabic_name", "english_name",
            "translated_name", "nuzool_location", "nuzool_order",
            "rukus", "total_ayas",
        ]
        for field in expected_fields:
            assert field in surah, f"Missing field: {field}"

    def test_surah_data_correct(self, client):
        resp = client.get(url("surahs"))
        surah = resp.json()[0]
        assert surah["english_name"] == "Al-Faatiha"
        assert surah["nuzool_location"] == "Meccan"


class TestGetTextTypes:
    def test_returns_text_types(self, client):
        resp = client.get(url("text-types"))
        assert resp.status_code == 200
        data = resp.json()
        assert "arabic" in data
        assert "english" in data

    def test_correct_text_types(self, client):
        resp = client.get(url("text-types"))
        data = resp.json()
        assert "simple-clean" in data["arabic"]
        assert "maududi" in data["english"]


class TestWordsByLetter:
    def test_returns_matching_words(self, client):
        # "الله" starts with "ا" (alif)
        resp = client.get(url("words-by-letter/ا"))
        assert resp.status_code == 200
        words = resp.json()
        assert len(words) > 0
        # Each item is [word, count]
        word_strings = [w[0] for w in words]
        assert "الله" in word_strings

    def test_empty_for_unused_letter(self, client):
        # "ط" (Taa) — unlikely in our small test data
        resp = client.get(url("words-by-letter/ط"))
        assert resp.status_code == 200
        words = resp.json()
        assert len(words) == 0

    def test_sorted_alphabetically(self, client):
        resp = client.get(url("words-by-letter/ا"))
        words = resp.json()
        if len(words) > 1:
            word_strings = [w[0] for w in words]
            assert word_strings == sorted(word_strings)


class TestAyasByWord:
    def test_found_word_returns_ayas(self, client):
        resp = client.get(url("ayas-by-word/الله/arabic:simple-clean"))
        assert resp.status_code == 200
        ayas = resp.json()
        assert len(ayas) > 0
        # Each aya has aya_key and texts
        assert "aya_key" in ayas[0]
        assert "texts" in ayas[0]

    def test_missing_word_returns_404(self, client):
        resp = client.get(url("ayas-by-word/كلمةغيرموجودة/arabic:simple-clean"))
        assert resp.status_code == 404

    def test_multi_language(self, client):
        resp = client.get(url("ayas-by-word/الله/arabic:simple-clean_english:maududi"))
        assert resp.status_code == 200
        ayas = resp.json()
        assert len(ayas) > 0
        # Should have both arabic and english texts
        first_aya = ayas[0]
        assert "arabic" in first_aya["texts"]
        assert "english" in first_aya["texts"]


class TestWordsByCount:
    def test_returns_matching_words(self, client):
        # "الرحمن" and "الرحيم" each appear 2 times in our test data
        resp = client.get(url("words-by-count/2"))
        assert resp.status_code == 200
        words = resp.json()
        assert len(words) > 0
        word_strings = [w[0] for w in words]
        assert "الرحمن" in word_strings

    def test_empty_for_impossible_count(self, client):
        resp = client.get(url("words-by-count/99999"))
        assert resp.status_code == 200
        words = resp.json()
        assert len(words) == 0


class TestAvailableWordCounts:
    def test_returns_count_list(self, client):
        resp = client.get(url("available-word-counts"))
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0
        # Each item has count and word_count
        assert "count" in data[0]
        assert "word_count" in data[0]

    def test_sorted_descending(self, client):
        resp = client.get(url("available-word-counts"))
        data = resp.json()
        counts = [d["count"] for d in data]
        assert counts == sorted(counts, reverse=True)


class TestTopMostFrequentWords:
    def test_respects_limit(self, client):
        resp = client.get(url("top-most-frequent-words/3"))
        assert resp.status_code == 200
        words = resp.json()
        assert len(words) <= 3

    def test_descending_order(self, client):
        resp = client.get(url("top-most-frequent-words/10"))
        words = resp.json()
        counts = [w[1] for w in words]
        assert counts == sorted(counts, reverse=True)


class TestGetText:
    def test_full_surah(self, client):
        resp = client.get(url("text/1/arabic:simple-clean"))
        assert resp.status_code == 200
        ayas = resp.json()
        assert len(ayas) == 3  # 3 ayas in surah 1

    def test_single_aya(self, client):
        resp = client.get(url("text/1:1/arabic:simple-clean"))
        assert resp.status_code == 200
        ayas = resp.json()
        assert len(ayas) == 1
        assert ayas[0]["aya_key"] == "1:1"

    def test_aya_range(self, client):
        resp = client.get(url("text/1:1-2/arabic:simple-clean"))
        assert resp.status_code == 200
        ayas = resp.json()
        assert len(ayas) == 2
        keys = [a["aya_key"] for a in ayas]
        assert "1:1" in keys
        assert "1:2" in keys

    def test_multi_language(self, client):
        resp = client.get(url("text/1:1/arabic:simple-clean_english:maududi"))
        assert resp.status_code == 200
        ayas = resp.json()
        assert len(ayas) == 1
        texts = ayas[0]["texts"]
        assert "arabic" in texts
        assert "english" in texts

    def test_empty_surah(self, client):
        # Surah 3 doesn't exist in test data
        resp = client.get(url("text/3/arabic:simple-clean"))
        assert resp.status_code == 200
        ayas = resp.json()
        assert len(ayas) == 0

    def test_text_content_correct(self, client):
        resp = client.get(url("text/1:1/arabic:simple-clean"))
        ayas = resp.json()
        arabic_text = ayas[0]["texts"]["arabic"]["simple-clean"]
        assert "بسم" in arabic_text


class TestSearch:
    def test_arabic_search(self, client):
        resp = client.get(url("search/الله/arabic:simple-clean/arabic:simple-clean"))
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) > 0
        # Each result has aya_key and texts
        assert "aya_key" in results[0]
        assert "texts" in results[0]

    def test_english_search(self, client):
        resp = client.get(url("search/Merciful/english:maududi/english:maududi"))
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) > 0

    def test_no_results(self, client):
        resp = client.get(url("search/xyznonexistent/arabic:simple-clean/arabic:simple-clean"))
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 0

    def test_with_translations(self, client):
        resp = client.get(url("search/الله/arabic:simple-clean/english:maududi"))
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) > 0
        first = results[0]
        # Should have both search language and translation
        assert "arabic" in first["texts"]
        assert "english" in first["texts"]
