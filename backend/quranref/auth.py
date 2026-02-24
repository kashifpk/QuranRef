from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from .auth_utils import create_access_token, verify_access_token
from .db import get_session
from .settings import get_settings
from .sql_models import User

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
async def callback(request: Request, session: Session = Depends(get_session)):
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
    stmt = (
        insert(User)
        .values(google_id=google_id, email=email, name=name, picture_url=picture_url)
        .on_conflict_do_update(
            index_elements=["google_id"],
            set_=dict(
                email=email,
                name=name,
                picture_url=picture_url,
                last_login=text("NOW()"),
            ),
        )
        .returning(User.id, User.email)
    )
    result = session.execute(stmt)
    row = result.one()
    session.commit()

    user_id, user_email = row
    jwt_token = create_access_token(user_id, user_email)

    response = RedirectResponse(url=settings.frontend_url)
    response.set_cookie(
        value=jwt_token, max_age=settings.jwt_expiry_hours * 3600, **_cookie_kwargs()
    )
    return response


@router.get("/me")
async def me(
    access_token: str | None = Cookie(default=None),
    session: Session = Depends(get_session),
):
    """Return current user info or null. Never returns 401."""
    if not access_token:
        return {"user": None}

    payload = verify_access_token(access_token)
    if not payload:
        return {"user": None}

    user_id = payload["sub"]
    user = session.get(User, user_id)

    if not user:
        return {"user": None}

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture_url": user.picture_url,
        }
    }


@router.post("/logout")
async def logout():
    """Clear the auth cookie."""
    response = JSONResponse(content={"ok": True})
    response.delete_cookie(**_cookie_kwargs())
    return response
