import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from . import API_BASE
from .api import router as api_router
from .auth import router as auth_router
from .bookmarks import router as bookmarks_router
from .settings import get_settings

app = FastAPI(
    title="QuranRef API",
    description="API for Quran Reference Application",
    version="2.0.0"
)

# Configure CORS for the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:41149",  # Local development frontend
        "https://quranref.info",   # Production frontend
        "https://www.quranref.info",  # Production frontend with www
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware (required by authlib for OAuth state)
settings = get_settings()
app.add_middleware(SessionMiddleware, secret_key=settings.jwt_secret_key)

# Include routers
app.include_router(api_router, prefix=API_BASE)
app.include_router(auth_router, prefix=API_BASE)
app.include_router(bookmarks_router, prefix=API_BASE)

# Determine static files directory
# In Docker: /code/static, locally: ../static relative to backend
STATIC_DIR = Path(os.environ.get("STATIC_DIR", Path(__file__).parent.parent.parent / "static"))
INDEX_HTML = STATIC_DIR / "index.html"

# Mount static files if directory exists (production)
if INDEX_HTML.exists():
    # Mount static assets (css, js, images, fonts)
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # Serve index.html for the root and all non-API routes (SPA support)
    @app.get("/")
    async def serve_frontend_root():
        """Serve the frontend SPA"""
        return FileResponse(INDEX_HTML)

    @app.get("/{path:path}")
    async def serve_frontend_spa(request: Request, path: str):
        """Serve frontend SPA - catch-all for client-side routing"""
        # Don't intercept API routes or docs
        if path.startswith(("api/", "docs", "redoc", "openapi.json")):
            return None

        # Check if it's a static file request
        static_file = STATIC_DIR / path
        if static_file.exists() and static_file.is_file():
            return FileResponse(static_file)

        # For all other routes, serve index.html (SPA client-side routing)
        return FileResponse(INDEX_HTML)
else:
    # Development mode - just show API info
    @app.get("/")
    async def root():
        """API root endpoint - health check"""
        return {
            "status": "ok",
            "message": "QuranRef API is running",
            "version": "2.0.0",
            "docs": "/docs",
            "note": "Frontend not found. Run 'bun run build' in frontend/ directory."
        }

DEV_PORT = 41148
