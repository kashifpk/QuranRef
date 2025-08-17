from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from . import API_BASE
from .api import router as api_router

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
        "*"  # Allow all origins for now (can be restricted later)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only the API router
app.include_router(api_router, prefix=API_BASE)

# Add a root endpoint for API health check
@app.get("/")
async def root():
    """API root endpoint - health check"""
    return {
        "status": "ok",
        "message": "QuranRef API is running",
        "version": "2.0.0",
        "docs": "/docs"
    }
