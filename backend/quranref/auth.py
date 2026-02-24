from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Cookie, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

from .auth_utils import create_access_token, verify_access_token
from .db import raw_connection
from .settings import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])

oauth = OAuth()

COOKIE_NAME = "access_token"


def _ensure_google_client():
    """Register Google OAuth client if not already registered. Raises 503 if not configured."""
    if "google" in oauth._registry:
        return
    settings = get_settings()
    if not settings.google_client_id:
        raise HTTPException(status_code=503, detail="Google OAuth is not configured")
    oauth.register(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


def _cookie_kwargs() -> dict:
    """Return cookie settings appropriate for the current environment."""
    settings = get_settings()
    return {
        "key": COOKIE_NAME,
        "httponly": True,
        "secure": settings.environment == "production",
        "samesite": "lax",
        "path": "/",
    }


@router.get("/login")
async def login(request: Request):
    """Redirect to Google OAuth consent screen."""
    _ensure_google_client()
    settings = get_settings()
    redirect_uri = f"{settings.backend_url}/api/v1/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback", name="auth_callback")
async def callback(request: Request):
    """Handle Google OAuth callback, upsert user, set JWT cookie, redirect to frontend."""
    _ensure_google_client()
    settings = get_settings()

    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo", {})

    google_id = userinfo["sub"]
    email = userinfo.get("email", "")
    name = userinfo.get("name", "")
    picture_url = userinfo.get("picture", "")

    # Upsert user
    with raw_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO users (google_id, email, name, picture_url) "
            "VALUES (%s, %s, %s, %s) "
            "ON CONFLICT (google_id) DO UPDATE SET "
            "email = EXCLUDED.email, name = EXCLUDED.name, "
            "picture_url = EXCLUDED.picture_url, last_login = NOW() "
            "RETURNING id, email",
            (google_id, email, name, picture_url),
        )
        row = cursor.fetchone()
        conn.commit()

    user_id, user_email = row
    jwt_token = create_access_token(user_id, user_email)

    response = RedirectResponse(url=settings.frontend_url)
    response.set_cookie(
        value=jwt_token, max_age=settings.jwt_expiry_hours * 3600, **_cookie_kwargs()
    )
    return response


@router.get("/me")
async def me(access_token: str | None = Cookie(default=None)):
    """Return current user info or null. Never returns 401."""
    if not access_token:
        return {"user": None}

    payload = verify_access_token(access_token)
    if not payload:
        return {"user": None}

    user_id = payload["sub"]
    with raw_connection() as conn:
        cursor = conn.execute(
            "SELECT id, email, name, picture_url FROM users WHERE id = %s",
            (user_id,),
        )
        row = cursor.fetchone()

    if not row:
        return {"user": None}

    return {
        "user": {
            "id": row[0],
            "email": row[1],
            "name": row[2],
            "picture_url": row[3],
        }
    }


@router.post("/logout")
async def logout():
    """Clear the auth cookie."""
    response = JSONResponse(content={"ok": True})
    response.delete_cookie(**_cookie_kwargs())
    return response
