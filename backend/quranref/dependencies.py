from fastapi import Cookie, HTTPException

from .auth_utils import verify_access_token


def get_current_user(access_token: str | None = Cookie(default=None)) -> dict | None:
    """Optional auth dependency. Returns JWT payload dict or None."""
    if not access_token:
        return None
    return verify_access_token(access_token)


def require_current_user(access_token: str | None = Cookie(default=None)) -> dict:
    """Strict auth dependency. Raises 401 if not authenticated."""
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = verify_access_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload
