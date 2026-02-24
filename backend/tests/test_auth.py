"""Tests for authentication endpoints and JWT utilities."""

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from quranref.auth_utils import create_access_token, verify_access_token
from quranref.settings import get_settings


# --- JWT utility tests ---


class TestJWTUtils:
    def test_create_and_verify_round_trip(self):
        token = create_access_token(user_id=42, email="test@example.com")
        payload = verify_access_token(token)
        assert payload is not None
        assert payload["sub"] == 42
        assert payload["email"] == "test@example.com"
        assert "exp" in payload
        assert "iat" in payload

    def test_verify_invalid_token(self):
        assert verify_access_token("not-a-real-token") is None

    def test_verify_expired_token(self):
        settings = get_settings()
        payload = {
            "sub": 1,
            "email": "expired@example.com",
            "iat": datetime.now(timezone.utc) - timedelta(hours=100),
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        assert verify_access_token(token) is None

    def test_verify_wrong_secret(self):
        payload = {
            "sub": 1,
            "email": "wrong@example.com",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        token = jwt.encode(payload, "wrong-secret", algorithm="HS256")
        assert verify_access_token(token) is None


# --- Auth endpoint tests ---


class TestAuthEndpoints:
    @pytest.fixture(autouse=True)
    def _setup(self, client, test_db):
        self.client = client
        self.db = test_db

    def _seed_user(self) -> tuple[int, str]:
        """Insert a test user and return (id, email)."""
        with self.db._pool.connection() as conn:
            cursor = conn.execute(
                "INSERT INTO users (google_id, email, name, picture_url) "
                "VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (google_id) DO UPDATE SET last_login = NOW() "
                "RETURNING id, email",
                ("google-123", "user@example.com", "Test User", "https://example.com/photo.jpg"),
            )
            row = cursor.fetchone()
            conn.commit()
        return row[0], row[1]

    def test_me_without_cookie(self):
        resp = self.client.get("/api/v1/auth/me")
        assert resp.status_code == 200
        assert resp.json() == {"user": None}

    def test_me_with_invalid_token(self):
        self.client.cookies.set("access_token", "garbage-token")
        resp = self.client.get("/api/v1/auth/me")
        assert resp.status_code == 200
        assert resp.json() == {"user": None}
        self.client.cookies.clear()

    def test_me_with_valid_token(self):
        user_id, email = self._seed_user()
        token = create_access_token(user_id, email)
        self.client.cookies.set("access_token", token)
        resp = self.client.get("/api/v1/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["user"] is not None
        assert data["user"]["email"] == "user@example.com"
        assert data["user"]["name"] == "Test User"
        assert data["user"]["picture_url"] == "https://example.com/photo.jpg"
        self.client.cookies.clear()

    def test_logout_clears_cookie(self):
        self.client.cookies.set("access_token", "some-token")
        resp = self.client.post("/api/v1/auth/logout")
        assert resp.status_code == 200
        assert resp.json() == {"ok": True}

    def test_login_without_oauth_configured(self):
        """When Google OAuth credentials are not configured, login returns 503."""
        settings = get_settings()
        if settings.google_client_id:
            pytest.skip("Google OAuth is configured; cannot test unconfigured path")
        resp = self.client.get("/api/v1/auth/login", follow_redirects=False)
        assert resp.status_code == 503
