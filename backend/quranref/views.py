from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse

from .template_config import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
