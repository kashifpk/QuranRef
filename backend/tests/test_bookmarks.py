"""Tests for bookmarks API endpoints."""

import pytest

from quranref.auth_utils import create_access_token


class TestBookmarksAPI:
    @pytest.fixture(autouse=True)
    def _setup(self, client, test_db):
        self.client = client
        self.db = test_db

    def _seed_user(self, google_id="google-bm-1", email="bm@example.com") -> tuple[int, str]:
        """Insert a test user and return (id, email)."""
        with self.db._pool.connection() as conn:
            cursor = conn.execute(
                "INSERT INTO users (google_id, email, name, picture_url) "
                "VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (google_id) DO UPDATE SET last_login = NOW() "
                "RETURNING id, email",
                (google_id, email, "Bookmark User", "https://example.com/photo.jpg"),
            )
            row = cursor.fetchone()
            conn.commit()
        return row[0], row[1]

    def _auth_cookie(self, user_id: int, email: str):
        token = create_access_token(user_id, email)
        self.client.cookies.set("access_token", token)

    def _cleanup_cookies(self):
        self.client.cookies.clear()

    def _cleanup_bookmarks(self, user_id: int):
        with self.db._pool.connection() as conn:
            conn.execute("DELETE FROM bookmarks WHERE user_id = %s", (user_id,))
            conn.commit()

    # --- Auth guard tests ---

    def test_list_bookmarks_unauthenticated(self):
        self._cleanup_cookies()
        resp = self.client.get("/api/v1/bookmarks")
        assert resp.status_code == 401

    def test_get_reading_unauthenticated(self):
        self._cleanup_cookies()
        resp = self.client.get("/api/v1/bookmarks/reading")
        assert resp.status_code == 401

    def test_put_reading_unauthenticated(self):
        self._cleanup_cookies()
        resp = self.client.put("/api/v1/bookmarks/reading", json={"aya_key": "1:1"})
        assert resp.status_code == 401

    def test_post_note_unauthenticated(self):
        self._cleanup_cookies()
        resp = self.client.post(
            "/api/v1/bookmarks/notes", json={"aya_key": "1:1", "note": "test"}
        )
        assert resp.status_code == 401

    # --- Empty state tests ---

    def test_list_bookmarks_empty(self):
        user_id, email = self._seed_user()
        self._auth_cookie(user_id, email)
        self._cleanup_bookmarks(user_id)

        resp = self.client.get("/api/v1/bookmarks")
        assert resp.status_code == 200
        data = resp.json()
        assert data["reading"] is None
        assert data["notes"] == []
        self._cleanup_cookies()

    def test_get_reading_empty(self):
        user_id, email = self._seed_user()
        self._auth_cookie(user_id, email)
        self._cleanup_bookmarks(user_id)

        resp = self.client.get("/api/v1/bookmarks/reading")
        assert resp.status_code == 200
        assert resp.json() is None
        self._cleanup_cookies()

    # --- Reading bookmark CRUD ---

    def test_set_reading_bookmark(self):
        user_id, email = self._seed_user()
        self._auth_cookie(user_id, email)
        self._cleanup_bookmarks(user_id)

        resp = self.client.put("/api/v1/bookmarks/reading", json={"aya_key": "1:1"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["bookmark_type"] == "reading"
        assert data["aya_key"] == "1:1"
        assert data["note"] == ""
        self._cleanup_bookmarks(user_id)
        self._cleanup_cookies()

    def test_replace_reading_bookmark(self):
        user_id, email = self._seed_user()
        self._auth_cookie(user_id, email)
        self._cleanup_bookmarks(user_id)

        self.client.put("/api/v1/bookmarks/reading", json={"aya_key": "1:1"})
        resp = self.client.put("/api/v1/bookmarks/reading", json={"aya_key": "2:5"})
        assert resp.status_code == 200
        assert resp.json()["aya_key"] == "2:5"

        # Only one reading bookmark should exist
        resp = self.client.get("/api/v1/bookmarks")
        assert resp.json()["reading"]["aya_key"] == "2:5"
        self._cleanup_bookmarks(user_id)
        self._cleanup_cookies()

    def test_delete_reading_bookmark(self):
        user_id, email = self._seed_user()
        self._auth_cookie(user_id, email)
        self._cleanup_bookmarks(user_id)

        self.client.put("/api/v1/bookmarks/reading", json={"aya_key": "1:1"})
        resp = self.client.delete("/api/v1/bookmarks/reading")
        assert resp.status_code == 204

        resp = self.client.get("/api/v1/bookmarks/reading")
        assert resp.json() is None
        self._cleanup_bookmarks(user_id)
        self._cleanup_cookies()

    def test_delete_reading_bookmark_when_none(self):
        user_id, email = self._seed_user()
        self._auth_cookie(user_id, email)
        self._cleanup_bookmarks(user_id)

        resp = self.client.delete("/api/v1/bookmarks/reading")
        assert resp.status_code == 204
        self._cleanup_cookies()

    # --- Note bookmark CRUD ---

    def test_add_note_bookmark(self):
        user_id, email = self._seed_user()
        self._auth_cookie(user_id, email)
        self._cleanup_bookmarks(user_id)

        resp = self.client.post(
            "/api/v1/bookmarks/notes", json={"aya_key": "1:2", "note": "Beautiful verse"}
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["bookmark_type"] == "note"
        assert data["aya_key"] == "1:2"
        assert data["note"] == "Beautiful verse"
        self._cleanup_bookmarks(user_id)
        self._cleanup_cookies()

    def test_add_multiple_notes(self):
        user_id, email = self._seed_user()
        self._auth_cookie(user_id, email)
        self._cleanup_bookmarks(user_id)

        self.client.post(
            "/api/v1/bookmarks/notes", json={"aya_key": "1:1", "note": "Note 1"}
        )
        self.client.post(
            "/api/v1/bookmarks/notes", json={"aya_key": "1:2", "note": "Note 2"}
        )

        resp = self.client.get("/api/v1/bookmarks")
        data = resp.json()
        assert len(data["notes"]) == 2
        self._cleanup_bookmarks(user_id)
        self._cleanup_cookies()

    def test_update_note_bookmark(self):
        user_id, email = self._seed_user()
        self._auth_cookie(user_id, email)
        self._cleanup_bookmarks(user_id)

        resp = self.client.post(
            "/api/v1/bookmarks/notes", json={"aya_key": "1:1", "note": "Original"}
        )
        note_id = resp.json()["id"]

        resp = self.client.put(
            f"/api/v1/bookmarks/notes/{note_id}", json={"note": "Updated"}
        )
        assert resp.status_code == 200
        assert resp.json()["note"] == "Updated"
        self._cleanup_bookmarks(user_id)
        self._cleanup_cookies()

    def test_delete_note_bookmark(self):
        user_id, email = self._seed_user()
        self._auth_cookie(user_id, email)
        self._cleanup_bookmarks(user_id)

        resp = self.client.post(
            "/api/v1/bookmarks/notes", json={"aya_key": "1:1", "note": "Delete me"}
        )
        note_id = resp.json()["id"]

        resp = self.client.delete(f"/api/v1/bookmarks/notes/{note_id}")
        assert resp.status_code == 204

        resp = self.client.get("/api/v1/bookmarks")
        assert len(resp.json()["notes"]) == 0
        self._cleanup_cookies()

    def test_delete_nonexistent_note(self):
        user_id, email = self._seed_user()
        self._auth_cookie(user_id, email)

        resp = self.client.delete("/api/v1/bookmarks/notes/999999")
        assert resp.status_code == 404
        self._cleanup_cookies()

    def test_update_nonexistent_note(self):
        user_id, email = self._seed_user()
        self._auth_cookie(user_id, email)

        resp = self.client.put(
            "/api/v1/bookmarks/notes/999999", json={"note": "Nope"}
        )
        assert resp.status_code == 404
        self._cleanup_cookies()

    # --- Validation tests ---

    def test_invalid_aya_key_format(self):
        user_id, email = self._seed_user()
        self._auth_cookie(user_id, email)

        resp = self.client.put("/api/v1/bookmarks/reading", json={"aya_key": "bad"})
        assert resp.status_code == 422
        self._cleanup_cookies()

    # --- Mixed bookmarks ---

    def test_reading_and_notes_together(self):
        user_id, email = self._seed_user()
        self._auth_cookie(user_id, email)
        self._cleanup_bookmarks(user_id)

        self.client.put("/api/v1/bookmarks/reading", json={"aya_key": "1:1"})
        self.client.post(
            "/api/v1/bookmarks/notes", json={"aya_key": "1:2", "note": "Reflection"}
        )

        resp = self.client.get("/api/v1/bookmarks")
        data = resp.json()
        assert data["reading"] is not None
        assert data["reading"]["aya_key"] == "1:1"
        assert len(data["notes"]) == 1
        assert data["notes"][0]["aya_key"] == "1:2"
        self._cleanup_bookmarks(user_id)
        self._cleanup_cookies()
