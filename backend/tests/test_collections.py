"""Tests for the collections API."""

import pytest
from quranref import API_BASE
from quranref.auth_utils import create_access_token


def url(path: str) -> str:
    return f"{API_BASE}/{path}"


class TestCollections:
    @pytest.fixture(autouse=True)
    def _setup(self, client, test_db):
        self.client = client
        self.db = test_db
        self.user_id, email = self._seed_user("google-col-1", "col@example.com")
        self.client.cookies.set("access_token", create_access_token(self.user_id, email))
        with self.db._pool.connection() as conn:
            conn.execute("DELETE FROM collections")
            conn.commit()
        yield
        self.client.cookies.clear()

    def _seed_user(self, google_id: str, email: str) -> tuple[int, str]:
        with self.db._pool.connection() as conn:
            row = conn.execute(
                "INSERT INTO users (google_id, email, name, picture_url) VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (google_id) DO UPDATE SET last_login = NOW() RETURNING id, email",
                (google_id, email, "Collector", ""),
            ).fetchone()
            conn.commit()
        return row[0], row[1]

    def _create(self, name="Mercy verses", description="") -> dict:
        resp = self.client.post(url("collections"), json={"name": name, "description": description})
        assert resp.status_code == 201, resp.text
        return resp.json()

    def test_requires_auth(self):
        self.client.cookies.clear()
        assert self.client.get(url("collections")).status_code == 401
        assert self.client.post(url("collections"), json={"name": "x"}).status_code == 401

    def test_create_list_and_duplicate_name(self):
        created = self._create(description="Ayas about mercy")
        assert created["item_count"] == 0 and created["aya_keys"] == []
        listing = self.client.get(url("collections")).json()
        assert [c["name"] for c in listing] == ["Mercy verses"]
        assert listing[0]["description"] == "Ayas about mercy"
        dup = self.client.post(url("collections"), json={"name": " Mercy verses "})
        assert dup.status_code == 409
        blank = self.client.post(url("collections"), json={"name": "   "})
        assert blank.status_code == 422

    def test_items_lifecycle(self):
        cid = self._create()["id"]
        first = self.client.post(url(f"collections/{cid}/items"), json={"aya_key": "1:1"})
        assert first.status_code == 201
        second = self.client.post(
            url(f"collections/{cid}/items"), json={"aya_key": "1:3", "note": "Repeated"}
        )
        assert second.status_code == 201
        assert second.json()["position"] == 1
        again = self.client.post(url(f"collections/{cid}/items"), json={"aya_key": "1:1"})
        assert again.status_code == 409
        bad = self.client.post(url(f"collections/{cid}/items"), json={"aya_key": "nope"})
        assert bad.status_code == 422

        detail = self.client.get(url(f"collections/{cid}")).json()
        assert [i["aya_key"] for i in detail["items"]] == ["1:1", "1:3"]
        summary = self.client.get(url("collections")).json()[0]
        assert summary["item_count"] == 2 and summary["aya_keys"] == ["1:1", "1:3"]

        item_id = second.json()["id"]
        updated = self.client.put(
            url(f"collections/{cid}/items/{item_id}"), json={"note": "See @1:1"}
        )
        assert updated.status_code == 200 and updated.json()["note"] == "See @1:1"

        reordered = self.client.put(url(f"collections/{cid}/order"), json={"item_ids": [item_id]})
        assert [i["aya_key"] for i in reordered.json()["items"]] == ["1:3", "1:1"]
        assert [i["position"] for i in reordered.json()["items"]] == [0, 1]

        page = self.client.get(
            url(f"collections/{cid}/ayas"), params={"languages": "arabic:simple-clean"}
        ).json()
        assert page["total"] == 2
        assert [a["aya_key"] for a in page["ayas"]] == ["1:3", "1:1"]
        assert page["ayas"][1]["texts"]["arabic"]["simple-clean"] == "بسم الله الرحمن الرحيم"
        paged = self.client.get(
            url(f"collections/{cid}/ayas"),
            params={"languages": "arabic:simple-clean", "offset": 1, "limit": 1},
        ).json()
        assert paged["offset"] == 1 and [a["aya_key"] for a in paged["ayas"]] == ["1:1"]
        assert self.client.get(url(f"collections/{cid}/ayas")).json()["ayas"] == []

        gone = self.client.delete(url(f"collections/{cid}/items/{item_id}"))
        assert gone.status_code == 204
        assert self.client.delete(url(f"collections/{cid}/items/{item_id}")).status_code == 404
        assert self.client.get(url(f"collections/{cid}")).json()["items"][0]["aya_key"] == "1:1"
        by_aya = self.client.delete(url(f"collections/{cid}/items/by-aya/1:1"))
        assert by_aya.status_code == 204
        assert self.client.delete(url(f"collections/{cid}/items/by-aya/1:1")).status_code == 404
        assert self.client.get(url("collections")).json()[0]["item_count"] == 0

    def test_rename_and_delete(self):
        cid = self._create()["id"]
        self._create("Other")
        renamed = self.client.put(url(f"collections/{cid}"), json={"name": "Rahma"})
        assert renamed.status_code == 200 and renamed.json()["name"] == "Rahma"
        clash = self.client.put(url(f"collections/{cid}"), json={"name": "Other"})
        assert clash.status_code == 409
        self.client.post(url(f"collections/{cid}/items"), json={"aya_key": "2:2"})
        assert self.client.delete(url(f"collections/{cid}")).status_code == 204
        assert self.client.get(url(f"collections/{cid}")).status_code == 404
        with self.db._pool.connection() as conn:
            count = conn.execute(
                "SELECT count(*) FROM collection_items WHERE collection_id = %s", (cid,)
            ).fetchone()[0]
        assert count == 0

    def test_other_users_collection_is_invisible(self):
        cid = self._create()["id"]
        other_id, other_email = self._seed_user("google-col-2", "other@example.com")
        self.client.cookies.set("access_token", create_access_token(other_id, other_email))
        assert self.client.get(url("collections")).json() == []
        assert self.client.get(url(f"collections/{cid}")).status_code == 404
        assert (
            self.client.post(url(f"collections/{cid}/items"), json={"aya_key": "1:1"}).status_code
            == 404
        )
        assert self.client.delete(url(f"collections/{cid}")).status_code == 404
