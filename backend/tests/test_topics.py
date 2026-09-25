"""Tests for the topics and themes endpoints."""

from quranref import API_BASE


def url(path: str) -> str:
    return f"{API_BASE}/{path}"


class TestTopics:
    def test_list_with_hierarchy(self, client):
        resp = client.get(url("topics"))
        assert resp.status_code == 200
        topics = {t["id"]: t for t in resp.json()}
        assert [t["name"] for t in resp.json()] == ["Allah", "Doctrine", "Mercy"]
        assert topics["2"]["thematic_parent_id"] == "3"
        assert topics["1"]["ontology_parent_id"] == "3"
        assert topics["3"]["thematic_parent_id"] is None
        assert topics["1"]["aya_count"] == 2

    def test_topic_page_rewrites_cross_links(self, client):
        resp = client.get(url("topic/1"))
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Allah"
        assert data["arabic_name"] == "الله"
        assert (
            data["description"]
            == '<b>Allah</b>, see <a href="/topic/2" class="topic-link">Mercy</a>.'
        )
        assert [p["name"] for p in data["parents"]] == ["Doctrine"]
        assert [r["name"] for r in data["related"]] == ["Mercy"]
        assert data["children"] == []

    def test_children_and_related_are_symmetric(self, client):
        data = client.get(url("topic/3")).json()
        assert [c["name"] for c in data["children"]] == ["Allah", "Mercy"]
        assert [r["name"] for r in client.get(url("topic/2")).json()["related"]] == ["Allah"]

    def test_unknown_topic(self, client):
        assert client.get(url("topic/999")).status_code == 404

    def test_topic_ayas_paginated_with_texts(self, client):
        resp = client.get(
            url("topic/1/ayas") + "?languages=arabic:simple-clean_english:maududi&limit=1"
        )
        assert resp.status_code == 200
        page = resp.json()
        assert page["total"] == 2
        assert [a["aya_key"] for a in page["ayas"]] == ["1:1"]
        assert page["ayas"][0]["texts"]["arabic"]["simple-clean"] == "بسم الله الرحمن الرحيم"
        assert "english" in page["ayas"][0]["texts"]
        second = client.get(url("topic/1/ayas") + "?languages=arabic:simple-clean&offset=1").json()
        assert [a["aya_key"] for a in second["ayas"]] == ["1:3"]

    def test_topics_for_ayas(self, client):
        resp = client.get(url("topics/for-ayas") + "?keys=1:1,1:3,2:2")
        assert resp.status_code == 200
        assert resp.json() == {"1:1": ["Allah", "Mercy"], "1:3": ["Allah"]}


class TestAyaTopicsAndThemes:
    def test_aya_topics_and_themes(self, client):
        data = client.get(url("aya-topics/1:1")).json()
        assert [t["name"] for t in data["topics"]] == ["Allah", "Mercy"]
        assert [(t["theme"], t["aya_from"], t["aya_to"]) for t in data["themes"]] == [
            ("Opening praise", 1, 3)
        ]

    def test_aya_without_topics(self, client):
        assert client.get(url("aya-topics/9:9")).json() == {"topics": [], "themes": []}

    def test_surah_themes_in_order(self, client):
        themes = client.get(url("themes/2")).json()
        assert [(t["theme"], t["keywords"]) for t in themes] == [("The Book", "book")]
        assert client.get(url("themes/9")).json() == []
