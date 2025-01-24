from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware

from . import API_BASE, PROJECT_ROOT
from .views import router as views_router
from .api import router as api_router
from .template_config import templates

app = FastAPI()

static_path = PROJECT_ROOT / "static"
app.mount('/static', StaticFiles(directory=static_path), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(views_router)
app.include_router(api_router, prefix=API_BASE)


@app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
async def catch_all(request: Request, full_path: str):
    """
    Catch all path to redirect to SPA style homepage on the frontend and let it handle the
    routing. This way backend routing takes precedence over frontend routing when pages are
    requested directly.
    """
    print(f"Catch all: {full_path}")
    return templates.TemplateResponse("index.html", {"request": request})
