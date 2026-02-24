from datetime import datetime, timedelta, timezone

import jwt

from .settings import get_settings


def create_access_token(user_id: int, email: str) -> str:
    """Create a JWT access token with user_id and email claims."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": now,
        "exp": now + timedelta(hours=settings.jwt_expiry_hours),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_access_token(token: str) -> dict | None:
    """Decode and validate a JWT token. Returns payload dict or None on any error."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        payload["sub"] = int(payload["sub"])
        return payload
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError, ValueError, KeyError):
        return None
