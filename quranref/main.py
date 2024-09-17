from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from . import API_BASE, PROJECT_ROOT
from .views import router as views_router
from .api import router as api_router

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

# @app.get("/")
# async def root():
#     return {"message": "Hello the World!"}
